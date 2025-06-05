#!/bin/bash
# a helper for deploying just solr pipeline for omca
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#

set -e
# make sure we do all this in the home directory
cd

echo "Refreshing OMCA Solr core $(date)"
gunzip -c -f 4solr.omca.public.csv.gz > 4solr.omca.public.csv
# || {die 'could not gunzip' ; exit 1;}
time ./solr-curl.sh
echo "done $(date)"
