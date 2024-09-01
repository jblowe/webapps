#!/bin/bash

MEDIA=/media/HDD3/cspacemedia/data
ORIGINALfile="$1"
OUTPUT_DIR="$2"
STATS="$3"

rm -f ${STATS}

while read -r BLOB MD5 LENGTH
do
  ((LINES++))
  D1="${MD5:0:2}"
  D2="${MD5:2:2}"
  convert ${MEDIA}/${D1}/${D2}/${MD5} -quality 80 -scale 600x\> ${OUTPUT_DIR}/${BLOB}.jpg
  RESIZED=$(stat -c "%s" ${OUTPUT_DIR}/${BLOB}.jpg)
  echo -e "${COUNTER}\t${BLOB}\t${MD5}\t${LENGTH}\t${RESIZED}" >> ${STATS}
done <  ${ORIGINALfile}

