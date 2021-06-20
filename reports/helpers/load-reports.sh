#!/bin/bash
#
if [ "$REPORTURL" == "" ] || [ "$REPORTUSER" == "" ]; then
    echo "REPORTURL and/or REPORTUSER environment variables are not set. Did you edit set-config.sh and 'source set-config.sh'?"
    exit
fi

if [ $# -ne 2 ]; then
    echo Usage: load-reports.sh listofreports.csv DocType
    exit
fi

if [ -r $1 ];
then
  for report in  `cut -f1 $1` ; do ./load-report.sh $report "$report" $2 ""; done 
else
  echo "$1 -- list of reports not found."
fi

