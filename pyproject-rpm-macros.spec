Name:           pyproject-rpm-macros
Version:        0
Release:        1%{?dist}
License:        MIT
Source0:        macros.pyproject
Source1:        README.md
Source2:        LICENSE
BuildArch:      noarch
Summary:        RPM macros for PEP 517 Python packages

Requires: python3-pip >= 19
Requires: python3-devel


%description
This is a provisional implementation of pyproject RPM macros for Fedora 30+.
These macros are useful for packaging Python projects that use the PEP 517
pyproject.toml file, which specifies the package's build dependencies
(including the build system, such as setuptools, flit or poetry).

%prep
cp -p %{SOURCE1} %{_builddir}
cp -p %{SOURCE2} %{_builddir}

%build
# nothing to do, sources are not buildable

%install
mkdir -p %{buildroot}/%{_rpmmacrodir}
install -m 644 %{SOURCE0} %{buildroot}/%{_rpmmacrodir}/

%files
%{_rpmmacrodir}/macros.pyproject

%doc README.md
%license LICENSE

%changelog

* Fri Jun 28 2019 Patrik Kopkan <pkopkan@redhat.com> - 0-1
- created package
