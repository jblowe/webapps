#!/usr/bin/env bash

for d in public internal
do
       CORE="omca-${d}"
       DATE=`tail -1 /var/log/django/omca/solr_extract_public.log | perl -ne 'if (/(Sun|Mon|Tue|Wed|Thu|Fri|Sat)/){print}else{print "PROBLEM: log file does not show a date as last line"}'`
       NUMFOUND=`curl -s -S "http://localhost:8983/solr/omca-${d}/select?q=*%3A*&rows=0&wt=json&indent=true" | grep numFound | perl -pe 's/.*"numFound":(\d+),.*/\1 rows/;'`
       STATUS=`grep '"status":' /var/log/django/omca/solr_extract_public.log | tail -1 | perl -ne 'unless (/.status.:0/) {print "\nNon-zero status from Solr:\n$_"}'`
       if [ "-v" == "$1" ] || [ `echo "$DATE" | grep -q "PROBLEM"` ] || [ "$STATUS" != "" ]            
       then
           echo "$CORE,$DATE,$NUMFOUND $STATUS"
       fi
done
