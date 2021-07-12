%global pypi_name pytest
Name:           python-%{pypi_name}

# For testing purposes, we package different versions on different Fedoras,
# because otherwise we would miss some dependencies (pytest 6.2 needs tox 3.20+)
# Please, don't write spec files like this in Fedora, it is forbidden.
%if 0%{?fedora} > 33 || 0%{?rhel} > 9
Version:        6.2.4
%else
Version:        4.4.2
%endif

Release:        0%{?dist}
Summary:        Simple powerful testing with Python
License:        MIT
URL:            https://pytest.org
Source0:        %{pypi_source}

%if v"%{version}" >= v"6.2"
# Fix Python 3.10 test issues
# Merged upstream, https://github.com/pytest-dev/pytest/pull/8555
# Rebased slightly
Patch2:         https://src.fedoraproject.org/rpms/pytest/raw/cad86f73367eff59a1d6daff44d262c3852f01f9/f/8555.patch
%endif

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
This is a pure Python package with executables. It has a test suite in tox.ini
and test dependencies specified via the [test] extra.
Building this tests:
- generating runtime and test dependencies by both tox.ini and extras
- pyproject.toml with the setuptools backend and setuptools-scm
- passing arguments into %%tox

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name}
%{summary}.


%prep
%autosetup -p1 -n %{pypi_name}-%{version}

# Remove duplicate '>=' in setup.cfg
# https://github.com/pytest-dev/pytest/pull/8336
# https://github.com/pytest-dev/pytest/pull/8774
sed -i 's/>=>=/>=/' setup.cfg


%generate_buildrequires
%pyproject_buildrequires -x testing -t

%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files '*pytest' +auto


%check
# Only run one test (which uses a test-only dependency, hypothesis)
# See how to pass options trough the macro to tox, trough tox to pytest
%tox -- -- -k metafunc


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst
%doc CHANGELOG.rst
%license LICENSE
