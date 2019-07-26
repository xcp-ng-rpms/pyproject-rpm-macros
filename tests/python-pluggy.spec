%global pypi_name pluggy
Name:           python-%{pypi_name}
Version:        0.12.0
Release:        1%{?dist}
Summary:        The plugin manager stripped of pytest specific details

License:        MIT
URL:            https://github.com/pytest-dev/pluggy
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  pyproject-rpm-macros

%description
%{summary}.


%package -n python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
%{summary}.


%prep
%autosetup -p1 -n %{pypi_name}-%{version}


%generate_buildrequires
%pyproject_buildrequires -t %{toxenv}-pytestrelease


%build
%pyproject_wheel


%install
%pyproject_install


%check
export PYTHONPATH=%{buildroot}%{python3_sitelib}
%{__python3} -m pytest


%files -n python3-%{pypi_name}
%doc README.rst
%license LICENSE
%{python3_sitelib}/%{pypi_name}/
%{python3_sitelib}/%{pypi_name}-%{version}.dist-info/
