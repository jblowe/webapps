#!/usr/bin/env bash

~/solr-etl/solrETL-public.sh        omca 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ~/solr-etl/logs/omca.solr_extract_public.log  2>&1
~/solr-etl/solrdatasources/omca/solrETL-internal.sh      omca 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ~/solr-etl/logs/omca.solr_extract_internal.log  2>&1
