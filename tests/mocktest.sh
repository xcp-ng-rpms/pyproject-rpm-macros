#!/usr/bin/bash -eux
. /etc/os-release
fedora=$VERSION_ID

pkgname=${1}
shift

config="/tmp/fedora-${fedora}-x86_64-ci.cfg"

# create mock config if not present
# this makes sure tested version of pyproject-rpm-macros is available
# TODO: check if it has precedence if the release was not bumped in tested PR
if [ ! -f $config ]; then
  original="/etc/mock/fedora-${fedora}-x86_64.cfg"
  cp $original $config

  echo -e '\n\n' >> $config
  echo -e 'config_opts["package_manager_max_attempts"] = 5' >> $config
  echo -e 'config_opts["package_manager_attempt_delay"] = 20' >> $config
  echo -e '\n\nconfig_opts[f"{config_opts.package_manager}.conf"] += """' >> $config

  # The zuul CI has zuul-build.repo
  # The Jenkins CI has test-<pkgname>.repo
  # We run this code from various packages, so we support any <pkgname>
  if [ -f /etc/yum.repos.d/zuul-build.repo ]; then
    cat /etc/yum.repos.d/zuul-build.repo >> $config
  else
    cat /etc/yum.repos.d/test-*.repo >> $config
  fi
  echo -e '\n"""\n' >> $config
fi

# prepare the rpmbuild folders, make sure nothing relevant is there
mkdir -p ~/rpmbuild/{SOURCES,SRPMS}
rm -f ~/rpmbuild/SRPMS/${pkgname}-*.src.rpm

# download the sources and create SRPM
spectool -g -R ${pkgname}.spec
rpmbuild -bs ${pkgname}.spec

# build the SRPM in mock
res=0
mock -r $config --enablerepo=local init
mock -r $config --enablerepo=local "$@" ~/rpmbuild/SRPMS/${pkgname}-*.src.rpm || res=$?

# move the results to the artifacts directory, so we can examine them
artifacts=${TEST_ARTIFACTS:-/tmp/artifacts}
pushd /var/lib/mock/fedora-*-x86_64/result
mv *.rpm ${artifacts}/ || :
for log in *.log; do
 mv ${log} ${artifacts}/${pkgname}-${log}
done
popd

exit $res
