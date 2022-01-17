Name:           python-getmac
Version:        0.8.3
Release:        0%{?dist}
Summary:        Get MAC addresses of remote hosts and local interfaces
License:        MIT
URL:            https://github.com/GhostofGoes/getmac
Source0:        %{pypi_source getmac}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros


%global _description %{expand:
Test that manpages are correctly processed by %%pyproject_save_files '*' +auto.}


%description %_description

%package -n     python3-getmac
Summary:        %{summary}

%description -n python3-getmac %_description


%prep
%autosetup -p1 -n getmac-%{version}


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files '*' +auto


%check
%pyproject_check_import
# Internal check for our macros, assert there is a manpage:
test -f %{buildroot}%{_mandir}/man1/getmac.1*


%files -n python3-getmac -f %{pyproject_files}

