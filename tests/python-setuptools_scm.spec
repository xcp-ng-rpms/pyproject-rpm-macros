Name:           python-setuptools_scm
Version:        3.5.0
Release:        0%{?dist}
Summary:        The blessed package to manage your versions by SCM tags
License:        MIT
URL:            https://github.com/pypa/setuptools_scm/
Source0:        %{pypi_source setuptools_scm}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Here we test that %%pyproject_extras_subpkg works and generates
setuptools_scm[toml] extra subpackage.

Note that it only works on Fedora 33+.

%package -n python3-setuptools_scm
Summary:        %{summary}

%description -n python3-setuptools_scm
...

%pyproject_extras_subpkg -n python3-setuptools_scm toml


%prep
%autosetup -p1 -n setuptools_scm-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files setuptools_scm


%check
# Internal check for our macros
# making sure that %%{pyproject_ghost_distinfo} has the right content
test -f %{pyproject_ghost_distinfo}
test "$(cat %{pyproject_ghost_distinfo})" == "%ghost %{python3_sitelib}/setuptools_scm-%{version}.dist-info"


%files -n python3-setuptools_scm -f %{pyproject_files}
%doc README.rst
%doc CHANGELOG.rst
%license LICENSE
