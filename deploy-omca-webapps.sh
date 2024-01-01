#!/bin/bash
# a helper for deploying the django webapps and solr pipelines for omca
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#

# make sure we do all this in the home directory
cd

OMCA_VERSION="$1"

echo "Deploying OMCA Solr pipelines"
YYYYMMDDHHMM=`date +%Y%m%d%H%M`
mv solr-pipelines ${YYYYMMDDHHMM}.solr-pipelines
cp -r ~/webapps/etl ~/solr-pipelines
cp solr-pipelines/utilities/checkstatus.sh ~

echo "Deploying OMCA webapps version ${OMCA_VERSION}"
~/webapps/setup.sh deploy omca prod latest "${OMCA_VERSION}"
