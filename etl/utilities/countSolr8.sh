#!/usr/bin/env bash
t=omca
for d in public internal
do
   if [[ `curl -s -S "http://localhost:8983/solr/${t}-${d}/admin/ping" | grep 'status'` =~ .*"OK".* ]]
   then
       CORE="${t}-${d}"
       NUMFOUND=`curl -s -S "http://localhost:8983/solr/${t}-${d}/select?q=*%3A*&rows=0&wt=json&indent=true" | grep numFound | perl -pe 's/.*"numFound":(\d+),.*/\1 rows/;'`
       echo "$CORE,$NUMFOUND"
   fi
done

