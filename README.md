pyproject RPM macros
====================

This is a provisional implementation of pyproject RPM macros for Fedora 30+.

These macros are useful for packaging Python projects that use the [PEP 517] `pyproject.toml` file, which specifies the package's build dependencies (including the build system, such as setuptools, flit or poetry).

[PEP 517]: https://www.python.org/dev/peps/pep-0517/


Usage
-----

If your upstream sources include `pyproject.toml` and you want to use these macros, BuildRequire them:

    BuildRequires: pyproject-rpm-macros

This will bring in python3-devel, so you don't need to require python3-devel explicitly.

Then, build a wheel in %build:

    %build
    %pyproject_wheel

And install the wheel in %install:

    %install
    %pyproject_install


Limitations
-----------

`%pyproject_install` currently installs all wheels in `$PWD`. We are working on a more explicit solution.

This macro changes shebang lines of every Python script in `%{buildroot}%{_bindir}` to `#! %{__python3} %{py3_shbang_opt}` (`#! /usr/bin/python -s`).
We plan to preserve exisiting Python flags in shebangs, but the work is not yet finished.

Currently, the macros do not automatically generate BuildRequires. We are working on that as well.

