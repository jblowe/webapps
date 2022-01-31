#!/bin/bash
#
#
# it presumes you have ssh access to either the prod or dev CSpace
# servers with your ssh keys set up for password-less login
#
# usually, these are yesterday's version (i.e. one day old, in /tmp)
#
# scps all the csv files for the Solr4 deployments
#
# caution: downloads serveral GB of compressed files!
# caution: this also fetches the 'internal' core extracts, which are sensitive!
#

if [ $# -ne 1 ]; then
    echo "Usage: ./scp4solr.sh <server>"
    echo
    echo "e.g. ./scp4solr.sh myusername@omca"
    exit
fi

scp -v $1:/tmp/4solr.*.gz .
gunzip -f 4solr.*.gz
