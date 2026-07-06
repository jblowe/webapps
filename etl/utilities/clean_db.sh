#!/usr/bin/env bash
DB=/home/webapps/projects/search_omca/db/production.sqlite3
echo "cleaning ${DB} at $(date)"
sqlite3 ${DB} 'select count(*) from searches;' 
sqlite3 ${DB} 'delete from searches;'
sqlite3 ${DB} 'vacuum;'
sqlite3 ${DB} 'select count(*) from searches;' 
echo "DONE cleaning ${DB} at $(date)"
