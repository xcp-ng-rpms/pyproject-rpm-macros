Name:           python-ldap
Version:        3.3.0
Release:        0%{?dist}
License:        Python
Summary:        An object-oriented API to access LDAP directory servers
Source0:        %{pypi_source}

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

BuildRequires:  cyrus-sasl-devel
BuildRequires:  gcc
BuildRequires:  openldap-clients
BuildRequires:  openldap-devel
BuildRequires:  openldap-servers
BuildRequires:  openssl-devel


%description
This package contains extension modules. Does not contain pyproject.toml.
Has multiple files and directories.
Building this tests:
- the proper files are installed in the proper places
- module glob in %%pyproject_save_files (some modules are included, some not)
- combined manual and generated Buildrequires


%package -n     python3-ldap
Summary:        %{summary}

%description -n python3-ldap
%{summary}


%prep
%autosetup


%generate_buildrequires
%pyproject_buildrequires -t


%build
%pyproject_wheel
# Internal check that we can import the built extension modules from %%{pyproject_build_lib}
! %{python3} -c 'import _ldap'
PYTHONPATH=%{pyproject_build_lib} %{python3} -c 'import _ldap'


%install
%pyproject_install
# We can pass multiple globs
%pyproject_save_files 'ldap*' '*ldap'


%check
%tox

# Internal check if the instalation outputs expected files
test -d %{buildroot}%{python3_sitearch}/__pycache__/
test -d %{buildroot}%{python3_sitearch}/python_ldap-%{version}.dist-info/
test -d %{buildroot}%{python3_sitearch}/ldap/
test -f %{buildroot}%{python3_sitearch}/ldapurl.py
test -f %{buildroot}%{python3_sitearch}/ldif.py
test -d %{buildroot}%{python3_sitearch}/slapdtest/
test -f %{buildroot}%{python3_sitearch}/_ldap.cpython-*.so

# Internal check: Unmatched modules are not supposed to be listed in %%{pyproject_files}
# We'll list them explicitly
! grep -F %{python3_sitearch}/ldif.py %{pyproject_files}
! grep -F %{python3_sitearch}/__pycache__/ldif.cpython-%{python3_version_nodots}.pyc %{pyproject_files}
! grep -F %{python3_sitearch}/__pycache__/ldif.cpython-%{python3_version_nodots}.opt-1.pyc %{pyproject_files}
! grep -F %{python3_sitearch}/slapdtest %{pyproject_files}

# Internal check: Top level __pycache__ is never owned
! grep -E '/site-packages/__pycache__$' %{pyproject_files}
! grep -E '/site-packages/__pycache__/$' %{pyproject_files}

# Internal check for the value of %%{pyproject_build_lib} in an archful package
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 10
test "%{pyproject_build_lib}" == "%{_builddir}/%{buildsubdir}/build/lib.%{python3_platform}-%{python3_version}"
%else
test "%{pyproject_build_lib}" == "$(echo %{_pyproject_builddir}/pip-req-build-*/build/lib.%{python3_platform}-%{python3_version})"
%endif


%files -n python3-ldap -f %{pyproject_files}
%license LICENCE
%doc CHANGES README TODO Demo
# Explicitly listed files can be combined with automation
%pycached %{python3_sitearch}/ldif.py
%{python3_sitearch}/slapdtest/
