#!/bin/bash
# a helper for deploying the django webapps for omca
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#

VERSION="$1"

# make sure the repos are clean and tidy and up to date
cd ~/webapps/
git pull -v
git checkout $VERSION

cd

echo "Deploying OMCA Solr pipelines"
YYYYMMDDHHMM=`date +%Y%m%d%H%M`
mv solr-pipelines ${YYYYMMDDHHMM}.solr-pipelines
cp -r ~/webapps/etl solr-pipelines
cp solr-pipelines/utilities/checkstatus.sh ~

rm -rf omca-clone
git clone https://github.com/cspace-deployment/cspace-webapps-common omca-clone

echo "Deploying OMCA webapps"
cd ~/omca-clone
~/webapps/setup.sh deploy omca prod latest
cd /var/www/omca
NEW_VERSION="base: $(tail -1 VERSION) omca: $VERSION"
echo "${NEW_VERSION}" > VERSION
touch /var/www/omca/cspace_django_site/wsgi.py
