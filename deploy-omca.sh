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

cd
rm -rf omca-clone
git clone https://github.com/cspace-deployment/cspace-webapps-common omca-clone


echo "Deploying OMCA webapps and Solr..."
cd omca-clone
~/webapps/setup.sh configure prod $VERSION
~/webapps/setup.sh deploy omca $VERSION
