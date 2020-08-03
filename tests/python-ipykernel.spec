Name:           python-ipykernel
Version:        5.2.1
Release:        0%{?dist}
Summary:        IPython Kernel for Jupyter
License:        BSD
URL:            https://github.com/ipython/ipykernel
Source0:        https://github.com/ipython/ipykernel/archive/v%{version}/ipykernel-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel

%description
This package contains data files.
Building this tests that data files are not listed when +auto is not used
with %%pyproject_save_files.

%package -n python3-ipykernel
Summary:        %{summary}

%description -n python3-ipykernel
...

%prep
%autosetup -p1 -n ipykernel-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files 'ipykernel*' +auto

%files -n python3-ipykernel -f %{pyproject_files}
%license COPYING.md
%doc README.md

