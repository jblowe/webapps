#!/bin/bash
date
##############################################################################
# reload a solr core (collection) using a file
##############################################################################
if [[ $# -lt 2 ]]; then
  echo "need at least TENANT and CORE as parameters!"
  echo "if a 3rd argument is provided, it is the solr extract to use"
  exit 1
fi
TENANT=$1
CORE=$2
CSVFILE=$3
TEMPFILE=temp_file
if [[ ${CSVFILE} ]]; then
  if [[ -f ${CSVFILE} ]]; then
    echo using the file you supplied, gunzipping it if necessary: ${CSVFILE}
  else
    echo "${CSVFILE} does not exist. abandoning ship..."
    exit 1
  fi
else
    CSVFILE="/tmp/4solr.${TENANT}.${CORE}.csv.gz"
    echo "trying to use yesterday's extract: ${CSVFILE}"
    if [[ ! -f ${CSVFILE} ]]; then
      echo "${CSVFILE} does not exist. abandoning ship..."
      exit 1
    fi
fi
# if it looks compressed, gunzip it. otherwise, try it as is
if [[  ${CSVFILE} =~ .*".gz" ]]; then
   gunzip -c ${CSVFILE} > ${TEMPFILE}
else
    cp ${CSVFILE} ${TEMPFILE}
fi
##############################################################################
# OK, let's roll!
##############################################################################
ROWS=`wc -l < temp_file`
curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
head -1 ${CSVFILE} | perl -pe 's/[\t\r]/\n/g' | perl -ne 'chomp; next unless /_(dt|s|i)s/; print "f.$_.split=true&f.$_.separator=%7C&"' > uploadparms.${TENANT}.${CORE}.tmp
ss_string=`cat uploadparms.${TENANT}.${CORE}.tmp`
time curl -X POST -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update/csv?commit=true&header=true&separator=%09&${ss_string}encapsulator=\\" -T temp_file -H 'Content-type:text/plain; charset=utf-8'
rm uploadparms.${TENANT}.${CORE}.tmp temp_file
date
