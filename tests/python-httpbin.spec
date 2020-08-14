Name:           python-httpbin
Version:        0.7.0
Release:        0%{?dist}
Summary:        HTTP Request & Response Service, written in Python + Flask
License:        MIT
URL:            https://github.com/Runscope/httpbin
Source0:        %{url}/archive/v%{version}/httpbin-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
This package buildrequires a package with extra: raven[flask].


%package -n python3-httpbin
Summary:            %{summary}

%if 0%{?fedora} < 33 && 0%{?rhel} < 9
# Old Fedoras don't understand Python extras yet
# This package needs raven[flask]
# So we add the transitive dependencies manually:
BuildRequires:  %{py3_dist blinker flask}
Requires:       %{py3_dist blinker flask}
%endif

%description -n python3-httpbin
%{summary}.


%prep
%autosetup -n httpbin-%{version}

# brotlipy wrapper is not packaged, httpbin works fine with brotli
sed -i s/brotlipy/brotli/ setup.py

# update test_httpbin.py to reflect new behavior of werkzeug
sed -i /Content-Length/d test_httpbin.py


%generate_buildrequires
%pyproject_buildrequires -t


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files httpbin


%check
%tox

# Internal check for our macros
# The runtime dependencies contain raven[flask], we assert we got them.
# The %%tox above also dies without it, but this makes it more explicit
%{python3} -c 'import blinker, flask'  # transitive deps


%files -n python3-httpbin -f %{pyproject_files}
%doc README*
%license LICENSE*
