%global pypi_name pytest
Name:           python-%{pypi_name}
Version:        4.4.2
Release:        0%{?dist}
Summary:        Simple powerful testing with Python
License:        MIT
URL:            https://pytest.org
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  pyproject-rpm-macros

%description
py.test provides simple, yet powerful testing for Python.


%package -n python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
py.test provides simple, yet powerful testing for Python.


%prep
%autosetup -p1 -n %{pypi_name}-%{version}


%generate_buildrequires
%pyproject_buildrequires -x testing -t


%build
%pyproject_wheel


%install
%pyproject_install

%check
# Only run one test (which uses a test-only dependency, hypothesis).
# (Unfortunately, some other tests still fail.)
%tox -- -- -k metafunc


%files -n python3-%{pypi_name}
%doc README.rst
%doc CHANGELOG.rst
%license LICENSE
%{_bindir}/pytest
%{_bindir}/py.test
%{python3_sitelib}/pytest-*.dist-info/
%{python3_sitelib}/_pytest/
%{python3_sitelib}/pytest.py
%{python3_sitelib}/__pycache__/pytest.*
