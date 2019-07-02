import sys

try:
    import pytoml
    from packaging.requirements import Requirement, InvalidRequirement
    from packaging.utils import canonicalize_name, canonicalize_version
except ImportError:
    # already echoed by the %pyproject_buildrequires macro
    sys.exit(0)


try:
    with open("pyproject.toml") as f:
        pyproject_data = pytoml.load(f)
except FileNotFoundError:
    pyproject_data = {}
except Exception as e:
    sys.exit(e)
else:
    import importlib

    try:
        backend = importlib.import_module(
            pyproject_data["build-system"]["build-backend"]
        )
    except KeyError:
        try:
            import setuptools.build_meta
        except ImportError:
            print("python3dist(setuptools) >= 40.8")
            print("python3dist(wheel)")
            sys.exit(0)

        backend = setuptools.build_meta
    except ImportError:
        backend = None


requirements = set()
rpm_requirements = set()


def add_requirement(requirement):
    try:
        requirements.add(Requirement(requirement))
    except InvalidRequirement as e:
        print(
            f"WARNING: Skipping invalid requirement: {requirement}\n         {e}",
            file=sys.stderr,
        )


if "requires" in pyproject_data.get("build-system", {}):
    try:
        for requirement in pyproject_data["build-system"]["requires"]:
            add_requirement(requirement)
    except Exception as e:
        sys.exit(e)


if hasattr(backend, "get_requires_for_build_wheel"):
    try:
        for requirement in backend.get_requires_for_build_wheel():
            add_requirement(requirement)
    except Exception as e:
        sys.exit(e)

for requirement in requirements:
    name = canonicalize_name(requirement.name)
    if requirement.marker is not None and not requirement.marker.evaluate():
        continue
    together = []
    for specifier in requirement.specifier:
        version = canonicalize_version(specifier.version)
        if specifier.operator == "!=":
            together.append(
                f"(python3dist({name}) < {version} or python3dist({name}) >= {version}.0)"
            )
        else:
            together.append(f"python3dist({name}) {specifier.operator} {version}")
    if len(together) == 0:
        rpm_requirements.add(f"python3dist({name})")
    if len(together) == 1:
        rpm_requirements.add(together[0])
    elif len(together) > 1:
        rpm_requirements.add(f"({' and '.join(together)})")


print(*sorted(rpm_requirements), sep="\n")
