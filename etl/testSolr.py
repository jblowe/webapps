import solr

# create a connection to a solr server
s = solr.SolrConnection('http://localhost:8983/solr/omca-public')

# do a search
response = s.query('text:canoe')
print(f'numFound: {response.numFound}')
for hit in response.results:
    # print(hit)
    print(hit['objectnumber_s'], hit['blob_ss'])
