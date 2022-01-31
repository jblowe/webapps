#!/usr/bin/env bash

for a in citationauthorities conceptauthorities orgauthorities personauthorities placeauthorities taxonomyauthority locationauthorities
#for a in citationauthorities
do
  ./extract_authorities.sh ${a} ${a}.xml
  python3 extractFromAuthority.py ${a}.xml ${a}.csv  items > ${a}-dups.txt

  if [[ -r ${a}.xml ]];
  then
    for item in  `cut -f4 ${a}.csv | perl -pe 's#/##'`
      do
        slug=${item/\//-}
        echo "$slug, $item"
        ./extract_authorities.sh ${item}/items ${slug}.xml
        python3 extractFromAuthority.py ${slug}.xml ${slug}.csv authority > ${slug}-dups.txt
      done
  else
    echo "${a}.xml -- authority XML file not found."
  fi

done

exit 1

tar -czf /tmp/authorities.tgz extracts/ucjeps-authorities 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
mv /tmp/authorities.tgz ~/extracts/ucjeps-authorities/authorities.tgz 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
