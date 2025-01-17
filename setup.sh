#!/bin/bash
#
# script to help deploy django webapps
#
# essentially a type of 'make' file.
#
# the project can be set up to run in Prod, Dev, and Pycharm environments with 'deploy'
#
# this bash script does the following:
#
# 1. 'deploy':
#     a. copies and configures the code for one of the 5 UCB deployments
#     b. "npm install" builds the needed js components
#     c. if running on a Linux server (i.e. ubuntu, which is detected automatically),
#        rsyncs the code to the runtime directory and makes symlinks in /var/www
# 2. other maintainance functions: 'disable' or 'enable' individual webapps
# 3. 'show' show what apps are installed

# exit on errors...
# TODO: uncomment this someday when the script really can be expected to run to completion without errors in all circumstances
# set -e
set -xv

export COMMAND=$1
# the second parameter can stand for 2 different things!
export WEBAPP=$2
export TENANT=$2
export DEPLOYMENT=$3

export VERSION="$4"
export OMCA_VERSION="$5"

export CONFIGDIR=${HOME}/webapps
export BASEDIR=${HOME}/cspace-webapps-common

# NB: we need python3, in fact python>=3.8 but the command for this varies from system to
# system. using 'python3' below works for OMCA deployments running Ubuntu 20.x
# YYMV!
export PYTHON=python3

# we don't export this value as others might be using it
YYYYMMDDHHMM=$(date +%Y%m%d%H%M)
export RUNDIR=${HOME}/${YYYYMMDDHHMM}/${TENANT}

function build_project() {

  if [[ ! -e manage.py ]]; then
    echo "No manage.py found. Something has gone wrong in the django project directory"
    echo
    exit 1
  fi

  # TODO: fix this hack to make the small amount of js work for all the webapps
  if [[ "$OSTYPE" == "linux-gnu" ]]; then
    perl -i -pe 's/..\/..\/suggest/\/$ENV{TENANT}\/suggest/' client_modules/js/PublicSearch.js
  fi
  # newer npm versions need this
  export NODE_OPTIONS=--openssl-legacy-provider

  # build the javascript
  npm install
  ./node_modules/.bin/webpack
  # disable eslint for now, until we address the errors it detects
  #./node_modules/.bin/eslint client_modules/js/app.js

  # TODO: for now, generate secret here and not in settings.py
  cd cspace_django_site
  $PYTHON -c "from secret_key_gen import *; generate_secret_key('secret_key.py');"
  cd ..
  # now we can go ahead and complete the configuration
  $PYTHON manage.py makemigrations
  $PYTHON manage.py migrate --noinput
  $PYTHON manage.py loaddata fixtures/*.json
  # get rid of the existing static_root to force django to rebuild it from scratch
  rm -rf static_root/
  $PYTHON manage.py collectstatic --noinput

  # the runtime directory is ${HOME}/YYYYMMDDHHMM/M
  # (where M is the museum and YYYYMMDDHHMM is today's date)
  # rsync the "prepped and configged" files to the runtime directory
  rsync -a --delete --exclude node_modules --exclude .git --exclude .gitignore . ${RUNDIR}
  NEW_VERSION="base: $(tail -1 VERSION) omca: ${OMCA_VERSION}"
  echo "${NEW_VERSION}" > ${RUNDIR}/VERSION

  # we assume the user has all the needed config files for this museum in ${HOME}/config
  rm -rf ${RUNDIR}/config/
  ln -s ${HOME}/config/${TENANT} ${RUNDIR}/config

  # on ubuntu servers, go ahead and symlink the runtime directory to
  # the location apache/passenger expects
  # then restart the webapps with 'touch'
  if [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo "symlinking ${RUNDIR} as /var/www/${TENANT}"
    rm -f /var/www/${TENANT}
    ln -s ${RUNDIR} /var/www/${TENANT}
    touch /var/www/${TENANT}/cspace_django_site/wsgi.py
  fi

  echo "*************************************************************************************************"
  echo "The configured CSpace system is:"
  grep 'hostname' ${RUNDIR}/config/main.cfg
  echo "*************************************************************************************************"
}

if [ $# -lt 2 -a "$1" != 'show' ]; then
  echo "Usage: $0 <enable|disable|deploy|show> <TENANT|CONFIGURATION|WEBAPP> <prod|dev|pycharm> (VERSION)"
  echo
  echo "where: TENANT = 'default' or the name of a deployable tenant"
  echo "       CONFIGURATION = <pycharm|dev|prod>"
  echo "       WEBAPP = one of the available webapps, e.g. 'search' or 'ireports'"
  echo "       VERSION = (optional) one of the available release candidates (tags)"
  echo
  echo "e.g. $0 disable ireports"
  echo "     $0 deploy omca prod webapps-6.1.0-rc8"
  echo "     $0 deploy omca pycharm"
  echo "     $0 show"
  echo
  exit 0
fi

if [[ "${COMMAND}" = "deploy" ]]; then

  if [[ ! -d "${CONFIGDIR}" ]]; then
    echo
    echo "The repo containing the configuration files (${CONFIGDIR}) does not exist"
    echo "Please either create it (e.g. by cloning it from github)"
    echo "or edit this script to set the correct path"
    echo
    exit 1
  else
    # make sure the OMCA repo is clean and tidy and up to date
    cd ${CONFIGDIR}
    git checkout main
    git pull -v
    git checkout ${OMCA_VERSION}  || { echo "could not checkout tag ${OMCA_VERSION}. Exiting. " ; exit 1; }
  fi

  if [[ ! -d "${CONFIGDIR}/${TENANT}" ]]; then
    echo
    echo "Can't deploy tenant ${TENANT}: ${CONFIGDIR}/${TENANT} does not exist"
    echo
    exit 1
  fi

  if [[ ! -d "${BASEDIR}" ]]; then
    echo
    echo "The repo containing the webapps (${BASEDIR}) does not exist"
    echo "Please either create it (e.g. by cloning it from github)"
    echo "or edit this script to set the correct path"
    echo
    exit 1
  else
    cd "${BASEDIR}"
  fi

  if [[ ! -f "cspace_django_site/extra_${DEPLOYMENT}.py" ]]; then
    echo
    echo "Can't configure '${DEPLOYMENT}': use 'pycharm', 'dev', or 'prod'"
    echo
    exit 1
  fi

  if [[ -e ${RUNDIR} ]]; then
    echo
    echo "Cowardly refusal to overwrite existing runtime directory ${RUNDIR}"
    echo "Remove or rename ${RUNDIR}, then try again."
    exit 1
  fi
  echo "Making and populating runtime directory ${RUNDIR}"
  mkdir -p ${RUNDIR}

  # ok, everything checks out... let's get going..

  # do all configuration in ${HOME}/working_dir, which is then rync'd to the runtime directory
  # if version is specified, make a 'clean' clone and checkout the tag
  # otherwise make copy of this exact repo and do the configuration work there
  rm -rf ${HOME}/working_dir
  if [[ $VERSION == "latest" ]]; then
    THIS_REPO=`git config --get remote.origin.url`
    git clone ${THIS_REPO} ${HOME}/working_dir
    cd ${HOME}/working_dir/
    LATEST_VERSION=$(git tag | grep -v "\-rc" | tail -1)
    git -c advice.detachedHead=false checkout ${LATEST_VERSION}
  else
    rsync -a . ${HOME}/working_dir
    cd ${HOME}/working_dir
  fi

  rm -f config/*
  rm -f fixtures/*

  # use 'default' configuration for this tenant from github, only initially, for configuration
  cp ${CONFIGDIR}/${TENANT}/config/* config
  cp ${CONFIGDIR}/${TENANT}/fixtures/* fixtures
  # note that in some cases, this cp will overwrite customized files in the underlying contributed apps
  # in cspace-webapps-common. that is the intended behavior!
  cp -r ${CONFIGDIR}/${TENANT}/apps/* .
  cp ${CONFIGDIR}/${TENANT}/project_urls.py cspace_django_site/urls.py
  cp ${CONFIGDIR}/${TENANT}/project_apps.py cspace_django_site/installed_apps.py
  cp ~/webapps/blacklight/public/header-logo-omca.png client_modules/static_assets/cspace_django_site/images/header-logo.png
  # cp client_modules/static_assets/cspace_django_site/images/header-logo-${TENANT}.png client_modules/static_assets/cspace_django_site/images/header-logo.png
  # just to be sure, we start over with the database...
  rm -f db.sqlite3

  # update the version file
  $PYTHON common/setversion.py

  # build js library, populate static dirs, rsync code to runtime dir if needed, etc.
  build_project
  echo
  echo "*************************************************************************************************"
  echo "Don't forget to check config/${TENANT}/main.cfg if necessary and the rest of the"
  echo "configuration files in config/ (these are .cfg, .json, and .csv files mostly)"
  echo "*************************************************************************************************"
  echo

  # reset repo to main branch
  cd ${CONFIGDIR}
  git checkout main

elif [[ "${COMMAND}" = "disable" ]]; then
  perl -i -pe "s/('${WEBAPP}')/# \1/" cspace_django_site/installed_apps.py
  perl -i -pe "s/(path)/# \1/ if /${WEBAPP}/" cspace_django_site/urls.py
  echo "Disabled ${WEBAPP}"
elif [[ "${COMMAND}" = "enable" ]]; then
  perl -i -pe "s/# *('${WEBAPP}')/\1/" cspace_django_site/installed_apps.py
  perl -i -pe "s/# *(path)/\1/ if /${WEBAPP}/" cspace_django_site/urls.py
  $PYTHON manage.py migrate --noinput
  $PYTHON manage.py collectstatic --noinput
  echo "Enabled ${WEBAPP}"
elif [[ "${COMMAND}" = "show" ]]; then
  echo
  echo "Installed apps:"
  echo
  echo -e "from cspace_django_site.installed_apps import INSTALLED_APPS\nfor i in INSTALLED_APPS: print(i)" | $PYTHON
  echo
else
  echo "${COMMAND} is not a recognized command."
fi
