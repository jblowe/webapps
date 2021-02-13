#!/usr/bin/env bash
##################################################################################
#
# "One Job To Rule Them All"
#
##################################################################################
#
# run all solr ETL
#
#
# 1. run the solr etl pipeline script
# 2. monitor solr datastore contents (i.e. send email etc. if needed)
#
##################################################################################
echo 'starting solr refresh' `date` >> refresh.log
./oj.omca.sh &
##################################################################################
# optimize all solrcores after refresh
##################################################################################
/home/app_solr/optimize.sh > /home/app_solr/logs/optimize.log
##################################################################################
# monitor solr datastores
##################################################################################
if [[ `./checkstatus.sh` ]] ; then ./checkstatus.sh -v | mail -s "PROBLEM with solr refresh nightly refresh" -- support@omca.org ; fi
./checkstatus.sh -v >> refresh.log
echo 'done with solr refresh' `date` >> refresh.log

