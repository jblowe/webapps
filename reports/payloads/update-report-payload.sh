#!/bin/bash

if [ "$REPORTURL" == "" ] || [ "$REPORTUSER" == "" ]; then
    echo "REPORTURL and/or REPORTUSER environment variables are not set. Did you edit set-config.sh and 'source set-config.sh'?"
    exit
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 reportcsid reportpayload.xml"
    exit
fi


REPORTCSID="$1"
PAYLOAD="$2"

time curl -s -S -v -X PUT --connect-timeout 900 -u "${REPORTUSER}" \
    -H "Content-Type: application/xml" \
    -T ${PAYLOAD} \
 ${REPORTURL}/cspace-services/reports/${REPORTCSID}

