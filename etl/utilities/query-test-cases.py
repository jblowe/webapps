import sys
from xml.etree import ElementTree as ET
import requests


def run(solr_url, query_terms_file):
    successes = 0
    failures = 0
    tested = 0
    with open(query_terms_file, 'r') as query_terms:
        for i, row in enumerate(query_terms):
            row = row.strip()
            if row == '': continue
            if row[0] == '#':
                print(row)
                continue
            query_terms = row.split('\t')
            row = row.replace('\t', ' vs ')
            if len(query_terms) != 2:
                print('expected two terms, separated by a tab: %s' % row)
                continue
            results = ['failed', 'failed']
            tested += 1
            for i, term in enumerate(query_terms):
                try:
                    url = '%s/select?q=text:%s&wt=xml' % (solr_url, term)
                    tree = ET.fromstring(requests.get(url).text)
                    num_found = tree.find('result')
                    num_found = int(num_found.attrib['numFound'])
                    results[i] = num_found
                except:
                    print('tried to test: %s' % row)
                    print('but query failed: %s' % url)
                    failures += 1
                    continue
            if results[0] == results[1] and 'failed' not in results:
                print("%s: %s OK" % (row, results[0]))
                successes += 1
            else:
                print("%s: %s does not equal %s" % (row, results[0], results[1]))
                failures += 1

        print()
        print("End of run. Pairs tested: %s, successes %s, failures %s" % (tested, successes, failures))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: %s url-of-solr-server list-of-terms.txt' % sys.argv[0])
        print(
            'e.g.  %s https://10.99.1.11/solr/pahma-public query-test-cases.omca.txt' % sys.argv[0])
        sys.exit(1)

    run(sys.argv[1], sys.argv[2])
