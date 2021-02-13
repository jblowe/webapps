#!/usr/bin/env bash

/home/app_solr/solrdatasources/omca/solrETL-public.sh        omca 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> /home/app_solr/logs/omca.solr_extract_public.log  2>&1
/home/app_solr/solrdatasources/omca/solrETL-internal.sh      omca 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> /home/app_solr/logs/omca.solr_extract_internal.log  2>&1
