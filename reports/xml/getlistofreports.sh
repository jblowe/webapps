eval `grep CREDS  credentials.cfg`
eval `grep SERVER  credentials.cfg`
curl -u ${CREDS} "${SERVER}/cspace-services/reports/?pgSz=100" | xmllint --format > reports.xml -
