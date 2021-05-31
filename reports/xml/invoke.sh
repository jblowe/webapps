CREDS=johnblowe@gmail.com:Uj53f#Skd6Ou
#curl -O -u ${CREDS} "http://10.161.2.194/cspace/omca/report/4c50a0c8-8f91-43f9-9d47?mode=single&csid=162bba00-fc74-4b58-9731-67cbcaebd345&outputMIME=application%2Fpdf&recordType=collectionobject"
curl -X POST -v -u ${CREDS} \
    -H "Content-Type: application/xml" \
    -d '<ns2:invocationContext xmlns:ns2="http://collectionspace.org/services/common/invocable"> \
  <mode>single</mode> \
  <docType>CollectionObject</docType> \
  <singleCSID>162bba00-fc74-4b58-9731-67cbcaebd345</singleCSID> \
</ns2:invocationContext>' \
 http://10.161.2.194/cspace-services/reports/4c50a0c8-8f91-43f9-9d47/invoke
