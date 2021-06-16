#!/bin/bash
set -x

eval `grep CREDS  credentials.cfg`
eval `grep SERVER credentials.cfg`

DOCTYPE="$1"
SINGLECSID="$2"
REPORTCSID="$3"

# e.g. curl -O -u ${CREDS} "${SERVER}/cspace/omca/report/4c50a0c8-8f91-43f9-9d47?mode=single&csid=162bba00-fc74-4b58-9731-67cbcaebd345&outputMIME=application%2Fpdf&recordType=collectionobject"
if [[ "${SINGLECSID}" = "all" ]]
then
    echo "nocontext for this report"
    D="<ns2:invocationContext xmlns:ns2=\"http://collectionspace.org/services/common/invocable\"> \
  <mode>nocontext</mode> \
  <docType>${DOCTYPE}</docType> \
  </ns2:invocationContext>"
else
    echo "single context ${SINGLECSID} for this report"
    D="<ns2:invocationContext xmlns:ns2=\"http://collectionspace.org/services/common/invocable\"> \
  <mode>single</mode> \
  <docType>${DOCTYPE}</docType> \
  <singleCSID>${SINGLECSID}</singleCSID> \
  </ns2:invocationContext>"
fi

curl -s -v -J -O --connect-timeout 900 -u ${CREDS} \
    -H "Content-Type: application/xml" \
    -d "$D" \
 ${SERVER}/cspace-services/reports/$REPORTCSID/invoke?impTimeout=900
# > $REPORTCSID.pdf
