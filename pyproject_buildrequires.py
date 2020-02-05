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
    import pytoml
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


@contextlib.contextmanager
def hook_call():
    captured_out = StringIO()
    with contextlib.redirect_stdout(captured_out):
        yield
    for line in captured_out.getvalue().splitlines():
        print_err('HOOK STDOUT:', line)


class Requirements:
    """Requirement printer"""
    def __init__(self, get_installed_version, extras=''):
        self.get_installed_version = get_installed_version

        self.marker_env = {'extra': extras}

        self.missing_requirements = False

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
                not requirement.marker.evaluate(environment=self.marker_env)):
            print_err(f'Ignoring alien requirement:', requirement_str)
            return

        try:
            installed = self.get_installed_version(requirement.name)
        except importlib_metadata.PackageNotFoundError:
            print_err(f'Requirement not satisfied: {requirement_str}')
            installed = None
        if installed and installed in requirement.specifier:
            print_err(f'Requirement satisfied: {requirement_str}')
            print_err(f'   (installed: {requirement.name} {installed})')
        else:
            self.missing_requirements = True

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
            if specifier.operator == '!=':
                lower = python3dist(name, '<', version)
                higher = python3dist(name, '>', f'{version}.0')
                together.append(
                    f'({lower} or {higher})'
                )
            else:
                together.append(python3dist(name, specifier.operator, version))
        if len(together) == 0:
            print(python3dist(name))
        elif len(together) == 1:
            print(together[0])
        else:
            print(f"({' and '.join(together)})")

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
        with f:
            pyproject_data = pytoml.load(f)

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
        sys.path.insert(0, backend_path)

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


def generate_tox_requirements(toxenv, requirements):
    requirements.add('tox-current-env >= 0.0.2', source='tox itself')
    requirements.check(source='tox itself')
    with tempfile.NamedTemporaryFile('r') as depfile:
        r = subprocess.run(
            ['tox', '--print-deps-to-file', depfile.name, '-qre', toxenv],
            check=False,
            encoding='utf-8',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if r.stdout:
            print_err(r.stdout, end='')
        r.check_returncode()
        requirements.extend(depfile.read().splitlines(),
                            source=f'tox --print-deps-only: {toxenv}')


def python3dist(name, op=None, version=None):
    if op is None:
        if version is not None:
            raise AssertionError('op and version go together')
        return f'python3dist({name})'
    else:
        return f'python3dist({name}) {op} {version}'


def generate_requires(
    *, include_runtime=False, toxenv=None, extras='',
    get_installed_version=importlib_metadata.version,  # for dep injection
):
    """Generate the BuildRequires for the project in the current directory

    This is the main Python entry point.
    """
    requirements = Requirements(get_installed_version, extras=extras)

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
        '-x', '--extras', metavar='EXTRAS', default='',
        help='extra for runtime requirements (e.g. -x testing)',
        # XXX: a comma-separated list should be possible here
        # help='comma separated list of "extras" for runtime requirements '
        #    + '(e.g. -x testing,feature-x)',
    )

    args = parser.parse_args(argv)

    if args.toxenv:
        args.tox = True

    if args.tox:
        args.runtime = True
        args.toxenv = (args.toxenv or os.getenv('RPM_TOXENV') or
                       f'py{sys.version_info.major}{sys.version_info.minor}')

    if args.extras and not args.runtime:
        print_err('-x (--extras) are only useful with -r (--runtime)')
        exit(1)

    try:
        generate_requires(
            include_runtime=args.runtime,
            toxenv=args.toxenv,
            extras=args.extras,
        )
    except Exception:
        # Log the traceback explicitly (it's useful debug info)
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
