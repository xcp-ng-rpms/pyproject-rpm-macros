%global pypi_name openqa_client
Name:           python-%{pypi_name}
Version:        4.0.0
Release:        1%{?dist}
Summary:        Python client library for openQA API

License:        GPLv2+
URL:            https://github.com/os-autoinst/openQA-python-client
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  pyproject-rpm-macros

%description
This package uses tox.ini file with recursive deps (via the -r option).

%package -n python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
%{summary}.


%prep
%autosetup -p1 -n %{pypi_name}-%{version}
# setuptools-git is needed to build the source distribution, but not
# for packaging, which *starts* from the source distribution
sed -i -e 's., "setuptools-git"..g' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires -t

%build
%pyproject_wheel

%install
%pyproject_install

%check
%tox


%files -n python3-%{pypi_name}
%doc README.*
%license COPYING
%{python3_sitelib}/%{pypi_name}/
%{python3_sitelib}/%{pypi_name}-%{version}.dist-info/
