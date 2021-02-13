#!/usr/bin/env bash
#
# redeploy the Solr ETL from github
#
if [[ $# -ne 1 ]] ;
then
  echo
  echo "Usage: $0 <version>"
  echo
  exit 1
fi

cd
SOLRETLDIR=~/solr
SOLR_REPO=~/omca_webapps/etl
# check to see we are plausibly able to do something...
if [ ! -d ${SOLR_REPO} ];
then
   echo "Solr repo ${SOLR_REPO} not found in this directory. Please clone from GitHub."
   exit 1
fi
if [ ! -d ${SOLRETLDIR} ];
then
   echo "Solr ETL directory $SOLRETLDIR not found. Assuming this is a fresh install"
else
    # make a backup of the current ETL directory just in case
    YYYYMMDD=`date +%Y%m%d`
    BACKUPDIR=${SOLRETLDIR}.${YYYYMMDD}
    if [ -d ${BACKUPDIR} ];
    then
       echo "Backup ETL directory ${BACKUPDIR} already exists. Please move or remove it and try again"
       exit 1
    fi
    mv ${SOLRETLDIR} ${BACKUPDIR}
fi

mkdir ${SOLRETLDIR}

# deploy fresh code from github
cd ${SOLR_REPO}
git checkout master
git pull -v
git checkout $1
cp utilities/o*.sh ~
cp utilities/checkstatus.sh ~

cd
rsync -a --exclude .git --exclude .gitignore --exclude solr-cores --exclude utilities ${SOLR_REPO}/ ${SOLRETLDIR}/

echo
echo "Solr ETL pipeline deploy complete."
echo
echo "Double-check configuration of code in ${SOLRETLDIR}!"
