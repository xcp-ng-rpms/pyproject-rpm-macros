Name:           fake-requirements
Version:        0
Release:        0%{?dist}

Summary:        ...
License:        MIT

BuildRequires:  pyproject-rpm-macros


%description 
Fake spec file to test %%pyproject_buildrequires -N works as expected

%prep
cat > requirements.txt <<EOF
click!=5.0.0,>=4.1 # comment to increase test complexity
toml>=0.10.0
EOF

%generate_buildrequires
%pyproject_buildrequires requirements.txt -N


%check
pip show toml click
! pip show setuptools
! pip show wheel

