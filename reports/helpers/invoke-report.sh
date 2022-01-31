REPORTCSID="$1"

D="<ns2:invocationContext xmlns:ns2=\"http://collectionspace.org/services/common/invocable\"> \
  <mode>single</mode> \
  <docType>CollectionObject</docType> \
  <singleCSID>999-999-999</singleCSID> \
  </ns2:invocationContext>"

time curl -s -v -J -O --connect-timeout 900 -u "${REPORTUSER}" \
    -H "Content-Type: application/xml" \
    -d "$D" \
 ${REPORTURL}/cspace-services/reports/${REPORTCSID}/invoke

