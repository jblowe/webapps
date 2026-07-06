#!/bin/bash -x
#
# Find new/changed blobs and sync them to s3.
#
# Requires BLOB_SERVICE_URL, BLOB_SERVICE_USER, BLOB_SERVICE_PASS in the
# environment. BLOB_SERVICE_USER/BLOB_SERVICE_PASS are BasicAuth credentials for the Blob Service.
#
#   BLOB_SERVICE_URL is a template containing the literal placeholder
#   "{blobcsid}", e.g.:
#     https://cspace.museumca.org/cspace-services/blobs/{blobcsid}/derivatives/Original/content
#
set -o pipefail

# --- config: edit here ---
SOLR_PIPELINES_DIR=~/solr-pipelines
SOLR_CSV_GZ=4solr.omca.media-public.csv.gz
LOCAL_CACHE=~/images
S3_BUCKET=s3://omca-media/thumbnails
UPDATE_LOG=s3_update.log

: "${BLOB_SERVICE_URL:?BLOB_SERVICE_URL must be set}"
: "${BLOB_SERVICE_USER:?BLOB_SERVICE_USER must be set}"
: "${BLOB_SERVICE_PASS:?BLOB_SERVICE_PASS must be set}"

SOLR_CSV="${SOLR_CSV_GZ%.gz}"

echo "s3 image update started $(date)" > ${UPDATE_LOG}
cd "${SOLR_PIPELINES_DIR}" || { echo "${SOLR_PIPELINES_DIR} does not exist" ; exit 1; }

# make a list of the images in the local 'cache'
ls ${LOCAL_CACHE} | perl -pe 's/\.jpg$//' | sort -u > s3_already_converted.csv
# make a list of the current public blobs
# (the list of public media is created as part of the solr refresh)
# column 8 = blobcsid (header row dropped since it's the literal word
# "blobcsid"; trailing solr row-count footer dropped via ' rows')
gunzip -fk "${SOLR_CSV_GZ}" || { echo "failed to unpack ${SOLR_CSV_GZ}" ; exit 1; }
cut -f8 "${SOLR_CSV}" | sort -u | grep -v blobcsid | grep -v ' rows' > s3_current_blobs.csv
# make a list of the public blobs that are not already in the local 'cache'
comm -23 s3_current_blobs.csv s3_already_converted.csv > s3_new_blobs.csv

# fetch each new blob from the Blob Service smaller jpeg for it in the
# local cache. Failures are reported (logged + recorded) and skipped, not fatal
STATS=s3_resize_stats.csv
FAILURES=s3_resize_failures.csv
rm -f "${STATS}" "${FAILURES}"

TMP_ORIGINAL=$(mktemp)
trap 'rm -f "${TMP_ORIGINAL}"' EXIT

CURL_TIMEOUT=30
LINES=0
while read -r BLOB
do
  ((LINES++))
  OUTPUT_FILE="${LOCAL_CACHE}/${BLOB}.jpg"
  REQUEST_URL="${BLOB_SERVICE_URL/\{blobcsid\}/${BLOB}}"

  HTTP_STATUS=$(curl -sS -o "${TMP_ORIGINAL}" -w '%{http_code}' \
    --user "${BLOB_SERVICE_USER}:${BLOB_SERVICE_PASS}" \
    --max-time "${CURL_TIMEOUT}" "${REQUEST_URL}")
  CURL_STATUS=$?

  if [[ ${CURL_STATUS} -ne 0 ]]; then
    echo -e "${LINES}\t${BLOB}\tfetch error (curl exit ${CURL_STATUS})" >> "${FAILURES}"
    continue
  fi
  case "${HTTP_STATUS}" in
    200) ;;
    404) echo -e "${LINES}\t${BLOB}\tblob not found (404)" >> "${FAILURES}"; continue ;;
    *)   echo -e "${LINES}\t${BLOB}\tfetch failed (http ${HTTP_STATUS})" >> "${FAILURES}"; continue ;;
  esac
  if [[ ! -s "${TMP_ORIGINAL}" ]]; then
    echo -e "${LINES}\t${BLOB}\tfetch returned empty body" >> "${FAILURES}"
    continue
  fi

  CONVERT_ERR=$(convert "${TMP_ORIGINAL}" -quality 80 -scale 600x\> "${OUTPUT_FILE}" 2>&1)
  CONVERT_STATUS=$?
  if [[ ${CONVERT_STATUS} -ne 0 ]]; then
    rm -f "${OUTPUT_FILE}"
    echo -e "${LINES}\t${BLOB}\tconvert failed: ${CONVERT_ERR//$'\n'/ }" >> "${FAILURES}"
    continue
  fi

  RESIZED=$(stat -c "%s" "${OUTPUT_FILE}")
  echo -e "${LINES}\t${BLOB}\t${RESIZED}" >> "${STATS}"
done < s3_new_blobs.csv

if [[ -s "${FAILURES}" ]]; then
  echo "WARNING: $(wc -l < "${FAILURES}") blob(s) failed to fetch/convert, see ${FAILURES}" >> ${UPDATE_LOG}
fi

# sync the new servable images to s3
# (nb: aws credentials need to be set up in the bash shell for this)
time aws s3 sync ${LOCAL_CACHE} ${S3_BUCKET} || { echo "aws s3 sync failed" ; exit 1; }

# make counts
wc -l s3_*.csv >> ${UPDATE_LOG}

# tidy up
rm -f "${SOLR_CSV}"
echo "s3 image update ended $(date)" >> ${UPDATE_LOG}
