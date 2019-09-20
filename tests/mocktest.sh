#!/usr/bin/bash -eux
. /etc/os-release
fedora=$VERSION_ID

# we don't have dynamic BuildRequires on Fedora 30
# so we at least test that we can build in a Fedora 31 mock
if [ $fedora -lt 31 ]; then
  fedora=31
fi

config="/tmp/fedora-${fedora}-x86_64-ci.cfg"

# create mock config if not present
# this makes sure tested version of pyproject-rpm-macros is available
# TODO: check if it has precedence if the release was not bumped in tested PR
if [ ! -f $config ]; then
  original="/etc/mock/fedora-${fedora}-x86_64.cfg"
  split=$(sed -n '/\[fedora\]/=' $original | head -n1)
  head -n$(($split-1)) $original > $config
  cat /etc/yum.repos.d/test-pyproject-rpm-macros.repo >> $config
  echo >> $config
  tail -n +$split $original >> $config
fi

# prepare the rpmbuild folders, make sure nothing relevant is there
mkdir -p ~/rpmbuild/{SOURCES,SRPMS}
rm -f ~/rpmbuild/SRPMS/${1}-*.src.rpm

# download the sources and create SRPM
spectool -g -R ${1}.spec
rpmbuild -bs ${1}.spec

# build the SRPM in mock
res=0
mock -r $config --enablerepo=local init
mock -r $config --enablerepo=local ~/rpmbuild/SRPMS/${1}-*.src.rpm || res=$?

# move the results to the artifacts directory, so we can examine them
artifacts=${TEST_ARTIFACTS:-/tmp/artifacts}
pushd /var/lib/mock/fedora-*-x86_64/result
mv *.rpm ${artifacts}/ || :
for log in *.log; do
 mv ${log} ${artifacts}/${1}-${log}
done
popd

exit $res
