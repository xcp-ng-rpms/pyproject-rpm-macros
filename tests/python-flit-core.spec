Name:           python-flit-core
Version:        3.0.0
Release:        0%{?dist}
Summary:        Distribution-building parts of Flit

License:        BSD
URL:            https://pypi.org/project/flit-core/
Source0:        %{pypi_source flit_core}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Test a build with pyproject.toml backend-path = .
flit-core builds with flit-core.


%package -n python3-flit-core
Summary:        %{summary}

%description -n python3-flit-core
...


%prep
%autosetup -p1 -n flit_core-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files flit_core


%files -n python3-flit-core -f %{pyproject_files}
