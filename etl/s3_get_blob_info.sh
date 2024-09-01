#!/bin/bash

while read -r BLOB
do
  ((LINES++))
  grep "${BLOB}" ${2}
done <  "$1"

