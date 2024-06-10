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
# nb: this moves the solr working directory and recreates it from
# scratch. simple, but do be careful if you change how it works.
YYYYMMDDHHMM=`date +%Y%m%d%H%M`
mv solr-pipelines ${YYYYMMDDHHMM}.solr-pipelines
cp -r ~/webapps/etl ~/solr-pipelines
cp ~/webapps/etl/utilities/checkstatus.sh ~

echo "Deploying OMCA webapps version ${OMCA_VERSION}"
# 'latest' means to deploy the latest release tag
~/webapps/setup.sh deploy omca prod latest "${OMCA_VERSION}"
