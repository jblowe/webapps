gunzip 4solr.omca.public.csv.gz 
cut -f 4,3,7,33,74,28,34,52,15,16,30,31,40,42,26,43,25,41,27,32,18,24,44,20,58,23 4solr.omca.public.csv > netx-extract.csv

python3 convert.py netx-extract.csv netxview.csv
psql -f create-netxview.sql
psql -f copy.sql

