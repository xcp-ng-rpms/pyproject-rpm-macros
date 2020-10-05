import os
import sys
import importlib
import argparse
import functools
import traceback
import contextlib
from io import StringIO
import subprocess
import re
import tempfile
import email.parser

print_err = functools.partial(print, file=sys.stderr)

# Some valid Python version specifiers are not supported.
# Whitelist characters we can handle.
VERSION_RE = re.compile('[a-zA-Z0-9.-]+')


class EndPass(Exception):
    """End current pass of generating requirements"""


try:
    from packaging.requirements import Requirement, InvalidRequirement
    from packaging.utils import canonicalize_name, canonicalize_version
    try:
        import importlib.metadata as importlib_metadata
    except ImportError:
        import importlib_metadata
except ImportError as e:
    print_err('Import error:', e)
    # already echoed by the %pyproject_buildrequires macro
    sys.exit(0)

# uses packaging, needs to be imported after packaging is verified to be present
from pyproject_convert import convert


@contextlib.contextmanager
def hook_call():
    captured_out = StringIO()
    with contextlib.redirect_stdout(captured_out):
        yield
    for line in captured_out.getvalue().splitlines():
        print_err('HOOK STDOUT:', line)


class Requirements:
    """Requirement printer"""
    def __init__(self, get_installed_version, extras=None,
                 generate_extras=False, python3_pkgversion='3'):
        self.get_installed_version = get_installed_version
        self.extras = set()

        if extras:
            for extra in extras:
                self.add_extras(*extra.split(','))

        self.missing_requirements = False

        self.generate_extras = generate_extras
        self.python3_pkgversion = python3_pkgversion

    def add_extras(self, *extras):
        self.extras |= set(e.strip() for e in extras)

    @property
    def marker_envs(self):
        if self.extras:
            return [{'extra': e} for e in sorted(self.extras)]
        return [{'extra': ''}]

    def evaluate_all_environamnets(self, requirement):
        for marker_env in self.marker_envs:
            if requirement.marker.evaluate(environment=marker_env):
                return True
        return False

    def add(self, requirement_str, *, source=None):
        """Output a Python-style requirement string as RPM dep"""
        print_err(f'Handling {requirement_str} from {source}')

        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement as e:
            print_err(
                f'WARNING: Skipping invalid requirement: {requirement_str}\n'
                + f'    {e}',
            )
            return

        name = canonicalize_name(requirement.name)
        if (requirement.marker is not None and
                not self.evaluate_all_environamnets(requirement)):
            print_err(f'Ignoring alien requirement:', requirement_str)
            return

        try:
            # TODO: check if requirements with extras are satisfied
            installed = self.get_installed_version(requirement.name)
        except importlib_metadata.PackageNotFoundError:
            print_err(f'Requirement not satisfied: {requirement_str}')
            installed = None
        if installed and installed in requirement.specifier:
            print_err(f'Requirement satisfied: {requirement_str}')
            print_err(f'   (installed: {requirement.name} {installed})')
            if requirement.extras:
                print_err(f'   (extras are currently not checked)')
        else:
            self.missing_requirements = True

        if self.generate_extras:
            extra_names = [f'{name}[{extra}]' for extra in sorted(requirement.extras)]
        else:
            extra_names = []

        for name in [name] + extra_names:
            together = []
            for specifier in sorted(
                requirement.specifier,
                key=lambda s: (s.operator, s.version),
            ):
                version = canonicalize_version(specifier.version)
                if not VERSION_RE.fullmatch(str(specifier.version)):
                    raise ValueError(
                        f'Unknown character in version: {specifier.version}. '
                        + '(This is probably a bug in pyproject-rpm-macros.)',
                    )
                together.append(convert(python3dist(name, python3_pkgversion=self.python3_pkgversion),
                                        specifier.operator, version))
            if len(together) == 0:
                print(python3dist(name,
                                  python3_pkgversion=self.python3_pkgversion))
            elif len(together) == 1:
                print(together[0])
            else:
                print(f"({' with '.join(together)})")

    def check(self, *, source=None):
        """End current pass if any unsatisfied dependencies were output"""
        if self.missing_requirements:
            print_err(f'Exiting dependency generation pass: {source}')
            raise EndPass(source)

    def extend(self, requirement_strs, *, source=None):
        """add() several requirements"""
        for req_str in requirement_strs:
            self.add(req_str, source=source)


def get_backend(requirements):
    try:
        f = open('pyproject.toml')
    except FileNotFoundError:
        pyproject_data = {}
    else:
        # lazy import toml here, not needed without pyproject.toml
        requirements.add('toml', source='parsing pyproject.toml')
        requirements.check(source='parsing pyproject.toml')
        import toml
        with f:
            pyproject_data = toml.load(f)

    buildsystem_data = pyproject_data.get('build-system', {})
    requirements.extend(
        buildsystem_data.get('requires', ()),
        source='build-system.requires',
    )

    backend_name = buildsystem_data.get('build-backend')
    if not backend_name:
        # https://www.python.org/dev/peps/pep-0517/:
        # If the pyproject.toml file is absent, or the build-backend key is
        # missing, the source tree is not using this specification, and tools
        # should revert to the legacy behaviour of running setup.py
        # (either directly, or by implicitly invoking the [following] backend).
        backend_name = 'setuptools.build_meta:__legacy__'

        requirements.add('setuptools >= 40.8', source='default build backend')
        requirements.add('wheel', source='default build backend')

    requirements.check(source='build backend')

    backend_path = buildsystem_data.get('backend-path')
    if backend_path:
        # PEP 517 example shows the path as a list, but some projects don't follow that
        if isinstance(backend_path, str):
            backend_path = [backend_path]
        sys.path = backend_path + sys.path

    module_name, _, object_name = backend_name.partition(":")
    backend_module = importlib.import_module(module_name)

    if object_name:
        return getattr(backend_module, object_name)

    return backend_module


def generate_build_requirements(backend, requirements):
    get_requires = getattr(backend, 'get_requires_for_build_wheel', None)
    if get_requires:
        with hook_call():
            new_reqs = get_requires()
        requirements.extend(new_reqs, source='get_requires_for_build_wheel')
        requirements.check(source='get_requires_for_build_wheel')


def generate_run_requirements(backend, requirements):
    hook_name = 'prepare_metadata_for_build_wheel'
    prepare_metadata = getattr(backend, hook_name, None)
    if not prepare_metadata:
        raise ValueError(
            'build backend cannot provide build metadata '
            + '(incl. runtime requirements) before buld'
        )
    with hook_call():
        dir_basename = prepare_metadata('.')
    with open(dir_basename + '/METADATA') as f:
        message = email.parser.Parser().parse(f, headersonly=True)
    for key in 'Requires', 'Requires-Dist':
        requires = message.get_all(key, ())
        requirements.extend(requires, source=f'wheel metadata: {key}')


def parse_tox_requires_lines(lines):
    packages = []
    for line in lines:
        line = line.strip()
        if line.startswith('-r'):
            path = line[2:]
            with open(path) as f:
                packages.extend(parse_tox_requires_lines(f.read().splitlines()))
        elif line.startswith('-'):
            print_err(
                f'WARNING: Skipping dependency line: {line}\n'
                + f'    tox deps options other than -r are not supported (yet).',
            )
        elif line:
            packages.append(line)
    return packages


def generate_tox_requirements(toxenv, requirements):
    requirements.add('tox-current-env >= 0.0.3', source='tox itself')
    requirements.check(source='tox itself')
    with tempfile.NamedTemporaryFile('r') as deps, tempfile.NamedTemporaryFile('r') as extras:
        r = subprocess.run(
            [sys.executable, '-m', 'tox',
             '--print-deps-to', deps.name,
             '--print-extras-to', extras.name,
             '-qre', toxenv],
            check=False,
            encoding='utf-8',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if r.stdout:
            print_err(r.stdout, end='')
        r.check_returncode()

        deplines = deps.read().splitlines()
        packages = parse_tox_requires_lines(deplines)
        requirements.add_extras(*extras.read().splitlines())
        requirements.extend(packages,
                            source=f'tox --print-deps-only: {toxenv}')


def python3dist(name, op=None, version=None, python3_pkgversion="3"):
    prefix = f"python{python3_pkgversion}dist"

    if op is None:
        if version is not None:
            raise AssertionError('op and version go together')
        return f'{prefix}({name})'
    else:
        return f'{prefix}({name}) {op} {version}'


def generate_requires(
    *, include_runtime=False, toxenv=None, extras=None,
    get_installed_version=importlib_metadata.version,  # for dep injection
    generate_extras=False, python3_pkgversion="3",
):
    """Generate the BuildRequires for the project in the current directory

    This is the main Python entry point.
    """
    requirements = Requirements(
        get_installed_version, extras=extras or [],
        generate_extras=generate_extras,
        python3_pkgversion=python3_pkgversion
    )

    try:
        backend = get_backend(requirements)
        generate_build_requirements(backend, requirements)
        if toxenv is not None:
            include_runtime = True
            generate_tox_requirements(toxenv, requirements)
        if include_runtime:
            generate_run_requirements(backend, requirements)
    except EndPass:
        return


def main(argv):
    parser = argparse.ArgumentParser(
        description='Generate BuildRequires for a Python project.'
    )
    parser.add_argument(
        '-r', '--runtime', action='store_true',
        help='Generate run-time requirements',
    )
    parser.add_argument(
        '-e', '--toxenv', metavar='TOXENVS', default=None,
        help=('specify tox environments'
              '(implies --tox)'),
    )
    parser.add_argument(
        '-t', '--tox', action='store_true',
        help=('generate test tequirements from tox environment '
              '(implies --runtime)'),
    )
    parser.add_argument(
        '-x', '--extras', metavar='EXTRAS', action='append',
        help='comma separated list of "extras" for runtime requirements '
             '(e.g. -x testing,feature-x) (implies --runtime, can be repeated)',
    )
    parser.add_argument(
        '--generate-extras', action='store_true',
        help='Generate build requirements on Python Extras',
    )
    parser.add_argument(
        '-p', '--python3_pkgversion', metavar='PYTHON3_PKGVERSION',
        default="3", help=('Python version for pythonXdist()'
                           'or pythonX.Ydist() requirements'),
    )

    args = parser.parse_args(argv)

    if args.toxenv:
        args.tox = True

    if args.tox:
        args.runtime = True
        args.toxenv = (args.toxenv or os.getenv('RPM_TOXENV') or
                       f'py{sys.version_info.major}{sys.version_info.minor}')

    if args.extras:
        args.runtime = True

    try:
        generate_requires(
            include_runtime=args.runtime,
            toxenv=args.toxenv,
            extras=args.extras,
            generate_extras=args.generate_extras,
            python3_pkgversion=args.python3_pkgversion,
        )
    except Exception:
        # Log the traceback explicitly (it's useful debug info)
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
