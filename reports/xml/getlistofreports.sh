CREDS=imageserver@museumca.org:digital15%
curl -u ${CREDS} "http://10.99.1.13:8180/cspace-services/reports/?pgSz=100" | xmllint --format > reports.xml -