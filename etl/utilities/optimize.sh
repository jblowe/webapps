time curl -S -s http://localhost:8983/solr/omca-internal/update --data '<optimize/>' -H 'Content-type:text/xml; charset=utf-8'
time curl -S -s http://localhost:8983/solr/omca-public/update --data '<optimize/>' -H 'Content-type:text/xml; charset=utf-8'
