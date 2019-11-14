Name:           tldr
Version:        0.4.4
Release:        3%{?dist}
Summary:        Simplified and community-driven man pages

License:        MIT
URL:            https://github.com/tldr-pages/tldr-python-client
Source0:        https://files.pythonhosted.org/packages/source/t/%{name}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros

%description
A Python command line client for tldr - Simplified and community-driven
man pages http://tldr-pages.github.io/.

%prep
%autosetup -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
sed -i '1{\=^#!/usr/bin/env python=d}' %{buildroot}%{python3_sitelib}/%{name}.py

%check
[ ! -d %{buildroot}%{_bindir}/__pycache__ ]

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}.py
%{python3_sitelib}/%{name}.py
%{python3_sitelib}/__pycache__/*.pyc
%{python3_sitelib}/%{name}-%{version}.dist-info
