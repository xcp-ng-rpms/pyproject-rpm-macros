Name:           pyproject-rpm-macros
Version:        0
Release:        2%{?dist}
License:        MIT
Source0:        macros.pyproject
Source1:        README.md
Source2:        LICENSE
URL:            https://src.fedoraproject.org/rpms/pyproject-rpm-macros
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
# Not strictly necessary but allows working on file names instead
# of source numbers in install section
%setup -c -T
cp -p %{sources} .

%build
# nothing to do, sources are not buildable

%install
mkdir -p %{buildroot}/%{_rpmmacrodir}
install -m 644 macros.pyproject %{buildroot}/%{_rpmmacrodir}/

%files
%{_rpmmacrodir}/macros.pyproject

%doc README.md
%license LICENSE

%changelog
* Tue Jul 02 2019 Miro Hrončok <mhroncok@redhat.com> - 0-2
- Fix shell syntax errors in %%pyproject_install
- Drop PATH warning in %%pyproject_install

* Fri Jun 28 2019 Patrik Kopkan <pkopkan@redhat.com> - 0-1
- created package
