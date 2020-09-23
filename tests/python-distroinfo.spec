Name:             python-distroinfo
Version:          0.3.2
Release:          0%{?dist}
Summary:          Parsing and querying distribution metadata stored in text/YAML files
License:          ASL 2.0
URL:              https://github.com/softwarefactory-project/distroinfo
Source0:          %{pypi_source distroinfo}
BuildArch:        noarch

BuildRequires:    pyproject-rpm-macros
BuildRequires:    python3-devel
BuildRequires:    python3-pytest
BuildRequires:    git-core

%description
This package uses setuptools and pbr.
It has setup_requires and tests that %%pyproject_buildrequires correctly
handles that including runtime requirements.

%package -n python3-distroinfo
Summary:          %{summary}

%description -n python3-distroinfo
...


%prep
%autosetup -p1 -n distroinfo-%{version}


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files distroinfo


%check
%pytest


%files -n python3-distroinfo -f %{pyproject_files}
%doc README.rst AUTHORS
%license LICENSE
