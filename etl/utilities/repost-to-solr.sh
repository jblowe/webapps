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
gunzip -c -f 4solr.omca.public.csv.gz > 4solr.omca.public.csv || { echo "ERROR: could not gunzip 4solr.omca.public.csv.gz" >&2; exit 1; }

lines=$(wc -l < 4solr.omca.public.csv)
# only reload the .csv file if it has more than 300,000 lines (i.e. a full file)
if [[ $lines -le 300000 ]]; then
    echo "ERROR: 4solr.omca.public.csv has only $lines line(s), aborting." >&2
    exit 1
fi

time ./solr-curl.sh
echo "done $(date)"
