#!/usr/bin/env bash

rm -f grid.html

while IFS=$'\t' read -r id label query count objectnumber pageurl imagefilename blurb; do
  if [ "$i" == "" ]; then
    i=0
    continue
  fi
  ((i += 1))
  # get the 'show pages' for the specified 'hero images' in the spreadsheet
  curl $pageurl >page.html

  # extract the url of the hero image and fetch it
  IMAGE_URL=$(grep 'show-image' page.html | head -1 | cut -f2 -d'"')

  curl -OJ ${IMAGE_URL}
  IMAGE_FILE=$(ls -tr | tail -1)
  THUMBNAIL="s$(printf "%02d" $i).jpg"

  #convert "${IMAGE_FILE}" -resample 150 -resize 3600x ${THUMBNAIL}
  #convert "${IMAGE_FILE}" -resize 360x ${THUMBNAIL}

  # cropped to square
  convert "${IMAGE_FILE}" \
    -resize 320x -resize 'x320<' \
    -gravity center -crop 320x320+0+0 +repage \
    ${THUMBNAIL}

  # not cropped
  #convert "${IMAGE_FILE}" \
  #      -resize 280x -resize 'x280<' \
  #      -gravity center +repage \
  #      ${THUMBNAIL}
  echo "$i,$objectnumber,$pageurl: ${IMAGE_FILE} ${THUMBNAIL}"

  echo "    <div class=\"gallery-item\">" >>grid.html
  echo "        <a href=\"${query}\">" >>grid.html
  echo "            <div class=\"thumb\"><img class=\"img-fluid\" src=\"${THUMBNAIL}\">" >>grid.html
  echo "                <br/><b>${label} ></b>" >>grid.html
  echo "            </div>" >>grid.html
  echo "        </a>" >>grid.html
  echo "    </div>" >>grid.html

done <$1
