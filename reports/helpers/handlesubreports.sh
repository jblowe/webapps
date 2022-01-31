# first, in the cspace reports directory, check if any
# of the supbreport .jasper files exist
sudo su - collectionspace
cd /opt/collectionspace/server/cspace/reports/
# collectionspace@cspace1804:/opt/collectionspace/server/cspace/reports$
ls -l subreport_*.jasper
# if they exist you probably do NOT have to recreate them, check carefully!
# if you do need to recreate them, delete the .jasper files. (consider
# backing them up, though, just in case
rm subreport_*.jasper
exit

# double check the .jrxml files are in fact there. if not,
# copy them from the webapps repo in ~webapps/reports/jrxml
ls -l subreport_*.jrxml

# become normal user again
exit
# become webapps user, cd to helpers directory
sudo su - webapps
cd webapps/reports/helpers/

# now, delete the report records if they exist (to be sure we make 'fresh ones')
# 'load' the subreports into cspace, execute each from the ui (to compile them)
# then delete them so the don't appear in the ui.

# set env vars (may need to edit the example file)
source set-config-omca.sh
# if any subreports exist, delete them all
./list-reports.sh > reports.txt
grep subreport reports.txt | cut -f1 > subreportstodelete.txt

# if subreportstodelete.txt has csids in it, delete the reports
wc -l subreportstodelete.txt

# delete delete delete
./delete-reports.sh subreportstodelete.txt

# reload them all
ls ~/webapps/reports/jrxml/subreport_*.jrxml | perl -pe 's/.jrxml//g;s/^.*\///' > subreportsjrxml.txt
./load-reports.sh subreportsjrxml.txt CollectionObject

# compile them in the UI: visit each report, run the report
# select any object record. mostly the reports will be empty, some may even fail.


sudo su - collectionspace
cd /opt/collectionspace/server/cspace/reports/
# collectionspace@cspace1804:/opt/collectionspace/server/cspace/reports$
ls -l subreport_*.jasper

# now delete the records so they will not be seen
./list-reports.sh > reports.txt
grep subreport reports.txt | cut -f1 > subreportstodelete.txt
./delete-all-reports.sh subreportstodelete.txt

# check to see that they are gone
./list-reports.sh > reports.txt
grep subreport reports.txt

# tidy up if you feel like it


