Name:           python-userpath
Version:        1.8.0
Release:        1%{?dist}
Summary:        Cross-platform tool for adding locations to the user PATH
License:        MIT
URL:            https://github.com/ofek/userpath
Source:         %{pypi_source userpath}
BuildArch:      noarch
BuildRequires:  python3-devel

%description
This package uses hatchling as build backend.
This package is tested because:

 - the prepare_metadata_for_build_wheel hook does not exist,
   %%pyproject_buildrequires -w is used
   https://github.com/ofek/hatch/issues/128
 - the licenses are stored in a dist-info subdirectory
   https://bugzilla.redhat.com/1985340
   (as of hatchling 0.22.0, not yet marked as License-File)


%package -n     python3-userpath
Summary:        %{summary}

%description -n python3-userpath
...


%if 0%{?fedora} > 34 || 0%{?rhel}
# On Fedora 34, we don't have hatchling, so this entire spec file builds nothing

%prep
%autosetup -p1 -n userpath-%{version}
sed -Ei '/^(coverage)$/d' requirements-dev.txt


%generate_buildrequires
%pyproject_buildrequires requirements-dev.txt -w


## %%pyproject_buildrequires -w makes this redundant:
#  %%build
#  %%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files userpath


%check
%pytest


%files -n python3-userpath -f %{pyproject_files}
%{_bindir}/userpath

%endif
