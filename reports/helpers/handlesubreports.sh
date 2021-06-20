# if any subreports exist, delete them all
./list-reports.sh > reports.txt
grep subreport reports.txt | cut -f1 > subreportstodelete.txt
./delete-all-reports.sh subreportstodelete.txt
# reload them all
ls ~/webapps/reports/jrxml/subreport_*.jrxml | perl -pe 's/.jrxml//g;s/^.*\///' > subreportsjrxml.txt
./load-reports.sh subreportsjrxml.txt CollectionObject
# compile them

# now delete the records so they will not be seen
./list-reports.sh > reports.txt
grep subreport reports.txt | cut -f1 > subreportstodelete.txt
./delete-all-reports.sh subreportstodelete.txt


