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
BuildRequires:  /usr/bin/git
BuildRequires:  /usr/bin/hg

%description
Here we test that %%pyproject_extras_subpkg works and generates
setuptools_scm[toml] extra subpackage.

Note that it only works on Fedora 33+.

We also check passing multiple -e flags to %%pyproject_buildrequires.
The tox environments also have a dependency on an extra ("toml").


%package -n python3-setuptools_scm
Summary:        %{summary}

%description -n python3-setuptools_scm
...

%pyproject_extras_subpkg -n python3-setuptools_scm toml


%prep
%autosetup -p1 -n setuptools_scm-%{version}

# there is a mistake in the flake8 environment configuration
# https://github.com/pypa/setuptools_scm/pull/444
# https://github.com/pypa/setuptools_scm/pull/489
sed -i -e 's@flake8 setuptools_scm/@flake8 src/setuptools_scm/@' -e 's@--exclude=setuptools_scm/@--exclude=src/setuptools_scm/@' tox.ini


%generate_buildrequires
%if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
# Note that you should not run flake8-like linters in Fedora spec files,
# here we do it solely to check the *ability* to use multiple toxenvs.
%pyproject_buildrequires -e %{default_toxenv}-test -e flake8
%else
# older Fedoras don't have the required runtime dependencies, so we don't test it there
%pyproject_buildrequires
%endif



%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files setuptools_scm


%check
%if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
# This tox should run all the toxenvs specified via -e in %%pyproject_buildrequires
# We only run some of the tests (running all of them requires network connection and is slow)
%tox -- -- -k test_version | tee toxlog

# Internal check for our macros: Assert both toxenvs were executed.
grep -F 'py%{python3_version_nodots}-test: commands succeeded' toxlog
grep -F 'flake8: commands succeeded' toxlog
%endif

# Internal check for our macros
# making sure that %%{pyproject_ghost_distinfo} has the right content
test -f %{pyproject_ghost_distinfo}
test "$(cat %{pyproject_ghost_distinfo})" == "%ghost %{python3_sitelib}/setuptools_scm-%{version}.dist-info"


%files -n python3-setuptools_scm -f %{pyproject_files}
%doc README.rst
%doc CHANGELOG.rst
%license LICENSE
