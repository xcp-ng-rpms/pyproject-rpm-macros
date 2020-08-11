Name:           python-requests
Version:        2.24.0
Release:        0%{?dist}
Summary:        Requests is an elegant and simple HTTP library for Python

License:        ASL 2.0
URL:            https://requests.readthedocs.io/
Source0:        %{pypi_source requests}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
This package uses multiple extras in %%pyproject_extras_subpkg and in
%%pyproject_buildrequires.


%package -n python3-requests
Summary:            %{summary}

%description -n python3-requests
%{summary}.


%pyproject_extras_subpkg -n python3-requests security socks


%prep
%autosetup -n requests-%{version}


%generate_buildrequires
%pyproject_buildrequires -x security,socks


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files requests


%check
# Internal check for our macros
# making sure that %%pyproject_buildrequires pulled in deps for both extras
%{python3} -c 'import cryptography, socks'


%files -n python3-requests -f %{pyproject_files}
%doc README.*
%license LICENSE
