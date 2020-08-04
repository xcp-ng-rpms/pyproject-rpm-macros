Name:           python-zope-event
Version:        4.2.0
Release:        0%{?dist}
Summary:        Zope Event Publication
License:        ZPLv2.1
URL:            https://pypi.python.org/pypi/zope.event/
Source0:        %{pypi_source zope.event}
BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel

%description
This package contains .pth files.
Building this tests that .pth files are not listed when +auto is not used
with %%pyproject_save_files.

%package -n python3-zope-event
Summary:       %{summary}

%description -n python3-zope-event
...

%prep
%setup -q -n zope.event-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files zope +auto

%files -n python3-zope-event -f %{pyproject_files}
%doc README.rst
%license LICENSE.txt

