Name:           escape_percentages
Version:        0
Release:        0
Summary:        ...
License:        MIT
BuildArch:      noarch

%description
This spec file verifies that escaping percentage signs in paths is possible via
exactly 8 percentage signs in a filelist and directly in the %%files section.
It serves as a regression test for pyproject_save_files:escape_rpm_path().
When this breaks, the function needs to be adapted.

%install
# the paths on disk will have 1 percentage sign if we type 2 in the spec
# we use the word 'version' after the sign, as that is a known existing macro
touch '%{buildroot}/one%%version'
touch '%{buildroot}/two%%version'

# the filelist will contain 8 percentage signs when we type 16 in spec
echo '/one%%%%%%%%%%%%%%%%version' > filelist
test $(wc -c filelist | cut -f1 -d' ') -eq 20  # 8 signs + /one (4) + version (7) + newline (1)

%files -f filelist
/two%%%%%%%%version
