# extract metadata and load into netxdb
source pgvars.sh
echo "copying 4solr.omca.public.csv.gz and extracting and massaging columns..."
cp ~webapps/solr-pipelines/4solr.omca.public.csv.gz .
gunzip -f 4solr.omca.public.csv.gz 
cut -f 4,3,7,33,74,28,34,52,15,16,30,31,40,42,26,43,25,41,27,32,18,24,44,20,58,23 4solr.omca.public.csv > netx-extract.csv
python convert.py netx-extract.csv netxview.csv
echo "`wc -l netxview.csv` rows (including header) extracted from '4solr file' containing `wc -l 4solr.omca.public.csv` lines"
psql -f create-netxview.sql
echo "netxview table recreated."

# TODO: for arrays, postgres hates unmatched curly braces inside array fields
perl -i -pe 's/\\"//g' netxview.csv
perl -i -pe "s/}'/'/g;s/ {/'/g;s/, *,/,/g" netxview.csv

psql -f copy.sql
rm 4solr.omca.public.csv  netx-extract.csv netxview.csv
