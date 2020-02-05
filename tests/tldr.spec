Name:           tldr
Version:        0.4.4
Release:        1%{?dist}
Summary:        Simplified and community-driven man pages

License:        MIT
URL:            https://github.com/tldr-pages/tldr-python-client
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  pyproject-rpm-macros

%description
%{summary}.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

%check
test ! -d %{buildroot}%{_bindir}/__pycache__
head -n1 %{buildroot}%{_bindir}/%{name}.py | egrep '#!\s*%{python3}\s+%{py3_shbang_opts}\s*$'

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}.py
%{python3_sitelib}/%{name}.py
%{python3_sitelib}/__pycache__/*.pyc
%{python3_sitelib}/%{name}-%{version}.dist-info/
