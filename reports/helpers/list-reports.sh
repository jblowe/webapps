#!/bin/bash
#
#
if [ "$REPORTURL" == "" ] || [ "$REPORTUSER" == "" ]; then
    echo "REPORTURL and/or REPORTUSER environment variables are not set. Did you edit set-config.sh and 'source set-config.sh'?"
    exit
fi

curl -s -S --stderr - --basic -u "$REPORTUSER" -X GET -H "Content-Type:application/xml" "$REPORTURL/cspace-services/reports?pgSz=1000" > curl.xml
perl -pe 's/<list/\n<list/g' curl.xml | perl -ne 'while (s/<list\-item>.*?<csid>(.*?)<.*?<name>(.*?)<.*?<filename>(.*?)<.*?<\/list\-item>//) { print "$2\t$1\t$3\n" }'
rm curl.xml
