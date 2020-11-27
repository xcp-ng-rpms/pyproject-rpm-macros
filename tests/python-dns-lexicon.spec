Name:           python-dns-lexicon

# For testing purposes, we package different versions on different Fedoras,
# because otherwise we would miss some dependencies.
# Please, don't write spec files like this in Fedora, it is forbidden.
%if 0%{?fedora} >= 34 || 0%{?rhel} >= 9
Version:        3.5.2
%else
Version:        3.4.0
%endif

Release:        0%{?dist}
Summary:        Manipulate DNS records on various DNS providers in a standardized/agnostic way
License:        MIT
URL:            https://github.com/AnalogJ/lexicon
Source0:        %{url}/archive/v%{version}/lexicon-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel

%description
This package has extras specified in tox configuration,
we test that the extras are installed when -e is used.
This package also uses a custom toxenv and creates several extras subpackages.


%package -n     python3-dns-lexicon
Summary:        %{summary}

%description -n python3-dns-lexicon
...


%pyproject_extras_subpackage -n python3-dns-lexicon plesk route53


%prep
%autosetup -n lexicon-%{version}
# The tox configuration lists a [dev] extra, but that installs nothing (is missing).
# The test requirements are only specified via poetry.dev-dependencies.
# Here we amend the data a bit so we can test more things, adding the tests deps to the dev extra:
sed -i \
's/\[tool.poetry.extras\]/'\
'pytest = {version = ">3", optional = true}\n'\
'vcrpy = {version = ">1", optional = true}\n\n'\
'[tool.poetry.extras]\n'\
'dev = ["pytest", "vcrpy"]/' pyproject.toml


%generate_buildrequires
%if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
# We use the "light" toxenv because the default one installs the [full] extra and we don't have all the deps.
# Note that [full] contains [plesk] and [route53] but we specify them manually instead:
%pyproject_buildrequires -e light -x plesk -x route53
%else
# older Fedoras don't have the required runtime dependencies, so we don't test it there
%pyproject_buildrequires
%endif


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files lexicon


%if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
%check
# we cannot use %%tox here, because the configured commands call poetry directly :/
# we use %%pytest instead, running a subset of tests not to waste CI time
%pytest -k "test_route53 or test_plesk"
%endif


%files -n python3-dns-lexicon -f %{pyproject_files}
%license LICENSE
%doc README.rst
%{_bindir}/lexicon
