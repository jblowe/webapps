#!/bin/bash
source /var/www/venv/bin/activate
# extract metadata and load into netxdb
echo "Data Source Sync starting `date`"
cd ~webapps/webapps/etc/dss2022
echo "copying 4solr.omca.internal.csv.gz and extracting and massaging columns..."
cp ~webapps/solr-pipelines/4solr.omca.internal.csv.gz .
gunzip -f 4solr.omca.internal.csv.gz
python convert.py 4solr.omca.internal.csv netxview.csv
echo "$(wc -l netxview.csv) rows (including header) extracted from '4solr file' containing $(wc -l 4solr.omca.internal.csv | cut -f1 -d" ") lines"
psql -h 10.161.2.192 -U netx -d netxdb -f create-netxview.sql
echo "netxview table recreated. copying data..."

psql -h 10.161.2.192 -U netx -d netxdb -f copy.sql
rm 4solr.omca.internal.csv netxview.csv
echo "Data Source Sync ended `date`"
