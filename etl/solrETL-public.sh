#!/bin/bash -x
date
##############################################################################
# move the current set of extracts to temp (thereby saving the previous run, just in case)
##############################################################################
mv 4solr.*.csv.gz /tmp
##############################################################################
# while most of this script is already tenant-specific, many of the commands
# are shared between the different scripts; having them be as similar as possible
# eases maintenance. ergo, the TENANT parameter
# password expected in .pgpass
##############################################################################
TENANT=$1
SERVER="localhost sslmode=prefer"
USERNAME="reader_${TENANT}"
DATABASE="${TENANT}_domain_${TENANT}"
CONNECTSTRING="host=$SERVER dbname=$DATABASE"
##############################################################################
# extract metadata and media info from CSpace
##############################################################################
# run the "media queries". psql's own --csv mode quotes any field containing
# the separator, a quote character, or a real newline (doubling embedded
# quotes), so there's no need for the old @@-record-separator trick or the
# perl newline-squashing that used to run on every query's output.
##############################################################################
time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f media-public.sql   > 4solr.${TENANT}.media-public.csv &
time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f media-internal.sql > 4solr.${TENANT}.media-internal.csv &
##############################################################################
# start the stitching process: extract the "basic" data
##############################################################################
time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f basic-public.sql > public.csv &
time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f basic-internal.sql > internal.csv &
wait
##############################################################################
# stitch this together with the results of the rest of the "subqueries"
# there are several query patterns which based on a couple of parameters
# will pull out multivalued fields, aggregate them, and spit them out with
# the top level object csid
#
# the patterns are in the template*.sql files
# the parameters are in the type*.txt files
##############################################################################
for TYPE in 1 2 3 4 5
do
  for var in `cat type${TYPE}.txt`
  do
    XTABLE=`echo $var | cut -d ',' -f 1`
    FIELD=`echo $var | cut -d ',' -f 2`
    perl -pe "s/XTABLE/${XTABLE}/g;s/FIELD/${FIELD}/g" template${TYPE}.sql > temp.sql
    time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f temp.sql > temp1.csv
    for CORE in public internal
    do
      time python3 join.py ${CORE}.csv temp1.csv > temp2.csv
      mv temp2.csv ${CORE}.csv
      # keep this intermediate file around for debugging, until the end of the run
      cp temp1.csv t${TYPE}.${var}.csv
    done
  done
done
##############################################################################
# these queries are special, the dont fit the patterns above
##############################################################################
for i in {1..20}
do
 if [ -f part$i.sql ]; then
   time psql --csv -U $USERNAME -d "$CONNECTSTRING" -f part$i.sql > part$i.csv
   time python3 join.py internal.csv part$i.csv > temp1.csv &
   time python3 join.py public.csv part$i.csv > temp2.csv &
   wait
   mv temp1.csv internal.csv
   mv temp2.csv public.csv
 fi
done
##############################################################################
#  compute a boolean: hascoords = yes/no
##############################################################################
# perl setCoords.pl 35 < d6.csv > d6a.csv
##############################################################################
#  mark the 16 'first' objects for the blacklight portal (public core only)
##############################################################################
python3 add_firsts.py public.csv temp.csv
mv temp.csv public.csv
##############################################################################
# add the blob and other media flags to the rest of the metadata
# and we want to recover and use our "special" solr-friendly header, which got buried
##############################################################################
for CORE in public internal
do
  # merge media and metadata files (done in perl ... very complicated to do in SQL)
  time perl mergeObjectsAndMedia.pl 4solr.${TENANT}.media-${CORE}.csv ${CORE}.csv hires_objectnumbers.csv "https://d6jfg2a0yiapu.cloudfront.net/hires"  > d6.csv
  # recover the solr header and put it back at the top of the file. use
  # head/tail (physical-line-based) rather than grep csid/-v csid here: a
  # quoted CSV field can legitimately contain an embedded newline, so a data
  # row can span more than one physical line, and grep would split it apart.
  # the header itself is always exactly one physical line (field names never
  # contain embedded newlines), so "first line" vs "everything else" is safe.
  head -1 d6.csv > header4Solr.csv
  # generate solr schema <copyField> elements, just in case.
  # also generate parameters for POST to solr (to split _ss fields properly)
  ./genschema.sh ${CORE}
  tail -n +2 d6.csv > d8.csv
  cat header4Solr.csv d8.csv | perl -pe 's/␥/|/g' > d9.csv
  ##############################################################################
  # compute _i values for _dt values (to support BL date range searching)
  ##############################################################################
  time python3 computeTimeIntegersOMCA.py d9.csv d10.csv
  ##############################################################################
  # normalize stray \r: decades of free-text museum records carry embedded
  # CR and CRLF line breaks (Windows/old-Mac authored notes). \r plays no
  # structural role in CSV (only \n, ',' and '"' do), so this is safe
  # everywhere, including inside a quoted field -- but Solr's CSV loader
  # apparently reads input line-by-line before its quote-aware parsing sees
  # it, and treats a bare \r (no following \n) as a line break on its own,
  # splitting a quoted multi-line field mid-record. collapse \r\n to \n and
  # turn any remaining lone \r into a space so no \r reaches Solr at all.
  ##############################################################################
  perl -i -pe 's/\r\n/\n/g; s/\r/ /g' d10.csv
  ##############################################################################
  # neutralize a Solr CSV loader bug: a field configured with
  # f.<field>.split=true (every _ss field, per genschema.sh below) breaks if
  # its value contains a literal " with more content after it -- Solr
  # mistakes the escaped quote pair for the field's real closing quote.
  # confirmed on Solr 9.4.0 and 9.9.0, so replace " with ' in just those
  # columns rather than waiting on an upstream fix.
  ##############################################################################
  python3 stripSplitFieldQuotes.py d10.csv d10q.csv && mv d10q.csv d10.csv
  ##############################################################################
  # check that all rows have the same number of fields as the header. this
  # must be CSV-quote-aware -- a legitimately quoted embedded comma would
  # make a naive comma split miscount -- so it uses evaluate.py rather than
  # awk. its "good rows" output becomes the file actually POSTed to Solr;
  # bad rows and per-column stats land in the counts file. runs against the
  # fully-assembled file, right before the POST, so nothing introduced by
  # mergeObjectsAndMedia.pl or computeTimeIntegersOMCA.py slips through.
  ##############################################################################
  time python3 evaluate.py d10.csv 4solr.${TENANT}.${CORE}.csv > 4solr.fields.${TENANT}.${CORE}.counts.csv
  ##############################################################################
  # also emit a plain, unencapsulated TSV of the same final data, for
  # anything downstream that wants tab-delimited output rather than quoted
  # CSV. scrubs tab/\r/\n out of every field (from the already-correctly-
  # parsed CSV, not by re-guessing row/column boundaries), so no
  # encapsulation is needed and no column can be pushed out of place.
  ##############################################################################
  time python3 csvToScrubbedTSV.py 4solr.${TENANT}.${CORE}.csv 4solr.${TENANT}.${CORE}.tsv &
  ##############################################################################
  # ok, now let's load this into solr...
  # clear out the existing data
  ##############################################################################
  curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
  curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
  ##############################################################################
  # this POSTs the csv to the Solr / update endpoint. standard RFC4180
  # quoting: comma separator, double-quote encapsulator (doubled internally).
  ##############################################################################
  ss_string=`cat uploadparms.${CORE}.txt`
  time curl -X POST -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update/csv?commit=true&header=true&separator=,&${ss_string}f.blob_ss.split=true&f.blob_ss.separator=,&encapsulator=%22" -T 4solr.${TENANT}.${CORE}.csv -H 'Content-type:text/plain; charset=utf-8' &
done
# wait for POSTs to Solr to finish
wait
##############################################################################
# wrap things up: make a gzipped version of what was loaded
##############################################################################
# get rid of intermediate files
rm -f temp*.csv temp.sql t?.*.csv d?.csv d10.csv m?.csv part*.csv schema*.xml header4Solr.csv public.csv internal.csv
# zip up .csvs, save a bit of space on backups
gzip -f 4solr.*.csv
date
