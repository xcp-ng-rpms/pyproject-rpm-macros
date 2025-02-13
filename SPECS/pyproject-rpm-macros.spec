%global package_speccommit ed24728a4f2f1fc31867e9f0fe7e79a7d5968b2e
%global usver 1.8.0
%global xsver 4
%global xsrel %{xsver}.1%{?xscount}%{?xshash}
Name:           pyproject-rpm-macros
Summary:        RPM macros for PEP 517 Python packages
License:        MIT

%bcond_with tests

# The idea is to follow the spirit of semver
# Given version X.Y.Z:
#   Increment X and reset Y.Z when there is a *major* incompatibility
#   Increment Y and reset Z when new macros or features are added
#   Increment Z when this is a bugfix or a cosmetic change
Version:        1.8.0
Release: %{?xsrel}%{?dist}

# Macro files
Source1: macros.pyproject
Source2: macros.aaa-pyproject-srpm

# Implementation files
Source101: pyproject_buildrequires.py
Source102: pyproject_save_files.py
Source103: pyproject_convert.py
Source104: pyproject_preprocess_record.py
Source105: pyproject_construct_toxenv.py
Source106: pyproject_requirements_txt.py
Source107: pyproject_wheel.py

# Tests
#Source201: pyproject_buildrequires.py
#Source202: pyproject_save_files.py
#Source203: pyproject_requirements_txt.py
Source204: compare_mandata.py

# Test data
Source301: pyproject_buildrequires_testcases.yaml
Source302: pyproject_save_files_test_data.yaml
Source303: test_RECORD

# Metadata
Source901: README.md
Source902: LICENSE
%define __python python3

URL:            https://src.fedoraproject.org/rpms/pyproject-rpm-macros

BuildArch:      noarch

%if %{with tests}
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(pytest-xdist)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(tox-current-env) >= 0.0.6
BuildRequires:  python3dist(wheel)
BuildRequires:  (python3dist(toml) if python3-devel < 3.11)
%endif

# We build on top of those:
BuildRequires:  python-rpm-macros
BuildRequires:  python-srpm-macros
BuildRequires:  epel-rpm-macros
Requires:       python-rpm-macros
Requires:       python-srpm-macros
Requires:       pyproject-srpm-macros = %{?epoch:%{epoch}:}%{version}-%{release}

# We use the following tools outside of coreutils
Requires:       findutils
Requires:       sed

%description
These macros allow projects that follow the Python packaging specifications
to be packaged as RPMs.

They work for:

* traditional Setuptools-based projects that use the setup.py file,
* newer Setuptools-based projects that have a setup.cfg file,
* general Python projects that use the PEP 517 pyproject.toml file
  (which allows using any build system, such as setuptools, flit or poetry).

These macros replace %%py3_build and %%py3_install,
which only work with setup.py.


%package -n pyproject-srpm-macros
Summary:        Minimal implementation of %%pyproject_buildrequires
Requires:       pyproject-rpm-macros = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n pyproject-srpm-macros
This package contains a minimal implementation of %%pyproject_buildrequires.
When used in %%generate_buildrequires, it will generate BuildRequires
for pyproject-rpm-macros. When both packages are installed, the full version
takes precedence.


%prep
# Not strictly necessary but allows working on file names instead
# of source numbers in install section
%setup -c -T
cp -p %{sources} .

%build
# nothing to do, sources are not buildable

%install
mkdir -p %{buildroot}%{_rpmmacrodir}
mkdir -p %{buildroot}%{_rpmconfigdir}/xenserver
install -pm 644 macros.pyproject %{buildroot}%{_rpmmacrodir}/
install -pm 644 macros.aaa-pyproject-srpm %{buildroot}%{_rpmmacrodir}/
install -pm 644 pyproject_buildrequires.py %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_convert.py %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_save_files.py  %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_preprocess_record.py %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_construct_toxenv.py %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_requirements_txt.py %{buildroot}%{_rpmconfigdir}/xenserver/
install -pm 644 pyproject_wheel.py %{buildroot}%{_rpmconfigdir}/xenserver/

%if %{with tests}
%check
export HOSTNAME="rpmbuild"  # to speedup tox in network-less mock, see rhbz#1856356
%pytest -vv --doctest-modules -n auto

# brp-compress is provided as an argument to get the right directory macro expansion
%{python3} compare_mandata.py -f %{_rpmconfigdir}/brp-compress
%endif


%files
%{_rpmmacrodir}/macros.pyproject
%{_rpmconfigdir}/xenserver/pyproject_buildrequires.py
%{_rpmconfigdir}/xenserver/pyproject_convert.py
%{_rpmconfigdir}/xenserver/pyproject_save_files.py
%{_rpmconfigdir}/xenserver/pyproject_preprocess_record.py
%{_rpmconfigdir}/xenserver/pyproject_construct_toxenv.py
%{_rpmconfigdir}/xenserver/pyproject_requirements_txt.py
%{_rpmconfigdir}/xenserver/pyproject_wheel.py

%doc README.md
%license LICENSE

%files -n pyproject-srpm-macros
%{_rpmmacrodir}/macros.aaa-pyproject-srpm
%license LICENSE


%changelog
* Thu Jan 23 2025 Yann Dirson <yann.dirson@vates.tech> - 1.8.0-4.1
- Add missing breq on epel-rpm-macros

* Fri Apr 12 2024 Bernhard Kaindl <bernhard.kaindl@cloud.com> - 1.8.0-4
- Fix {,.opt-?} in generated file names and error from license labels
* Thu Jun 08 2023 Tim Smith <tim.smith@citrix.com> - 1.8.0-1
- First imported release
