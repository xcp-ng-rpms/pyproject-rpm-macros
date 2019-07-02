pyproject RPM macros
====================

This is a provisional implementation of pyproject RPM macros for Fedora 30+.

These macros are useful for packaging Python projects that use the [PEP 517] `pyproject.toml` file, which specifies the package's build dependencies (including the build system, such as setuptools, flit or poetry).


Usage
-----

If your upstream sources include `pyproject.toml` and you want to use these macros, BuildRequire them:

    BuildRequires: pyproject-rpm-macros

This will bring in python3-devel, so you don't need to require python3-devel explicitly.

In order to get automatic build dependencies on Fedora 31+, run `%pyproject_buildrequires` in the `%generate_buildrequires` section:

    %generate_buildrequires
    %pyproject_buildrequires

Only build dependencies according to [PEP 517] and [PEP 518] will be added.
All other build dependencies (such as non-Python libraries or test dependencies) still need to be specified manually.

Then, build a wheel in `%build` with `%pyproject_wheel`:

    %build
    %pyproject_wheel

And install the wheel in `%install` with `%pyproject_install`:

    %install
    %pyproject_install


Limitations
-----------

`%pyproject_install` currently installs all wheels in `$PWD`. We are working on a more explicit solution.

This macro changes shebang lines of every Python script in `%{buildroot}%{_bindir}` to `#! %{__python3} %{py3_shbang_opt}` (`#! /usr/bin/python3 -s`).
We plan to preserve existing Python flags in shebangs, but the work is not yet finished.

The PEPs don't (yet) define a way to specify test dependencies and test runners.
That means you still need to handle test dependencies and `%check` on your own.


[PEP 517]: https://www.python.org/dev/peps/pep-0517/
[PEP 518]: https://www.python.org/dev/peps/pep-0518/
