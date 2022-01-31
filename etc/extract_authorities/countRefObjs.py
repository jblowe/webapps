import requests
import yaml
# import xml.etree.ElementTree as ET
from lxml import etree as ET
import os, sys, csv, codecs, logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


if len(sys.argv) != 5:
    print("")
    print("reads a csv file with CSID as 1st column, annnotates it with counts of refObjs")
    print("")
    print("usage: python %s <configfile.yml> <inputfile.csv> <outputfile.csv> <uri>" % sys.argv[0])
    print("")
    print("e.g:   python %s organization.csv organization-w-refobjs.csv citationauthorities/e6cb9bfa-724d-476c-be22" % sys.argv[0])
    exit(1)


with open(sys.argv[1], 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        SERVER = config['SERVER']
        CREDS = config['CREDS']
        credentials = tuple(CREDS.split(':'))
    except yaml.YAMLError as exc:
        logging.info(exc)

# http://10.161.2.194/cspace-services/citationauthorities/e6cb9bfa-724d-476c-be22/items/b90c33bc-7e0a-437f-8e98-7d986826d123/refObjs
try:
    csidsRows = csv.reader(open(sys.argv[2], 'r'), delimiter='\t')
except:
    print(sys.stderr, 'could not read or parse input file for CSIDs')
    exit(0)

cspaceCSV = csv.writer(open(sys.argv[3], 'w'), delimiter='\t')

RECORD = sys.argv[4]
PAGESIZE=1

def extract_tag(xml, tag):
    element = xml.find('.//%s' % tag)
    return element.text

for row in csidsRows:
    csid = row[1]
    url = f'{SERVER}/cspace-services/{RECORD}/items/{csid}/refObjs?pgSz={PAGESIZE}&pgNum=0'
    r = requests.get(url, auth=credentials)
    if r.status_code != 200:
        logging.info(f'status code for List GET is {r.status_code}, not 200. Cannot continue. url is {url}')
        break
    try:
        cspaceXML = ET.XML(r.text.encode('utf-8'))
    except:
        logging.info(f'could not parse response for {url}')
        logging.info('check credentials? etc?')
        logging.info(r.text)
        raise
    # if we get no items, we are done
    totalItems = int(cspaceXML.find('.//totalItems').text)
    cspaceCSV.writerow([totalItems] + row)


def keepfornow(FIELDS):
    items = cspaceXML.findall('.//authority-ref-doc-item')

    number_updated = 0
    for list_item in items:
        uri = list_item.find('.//uri').text

        url = f'{SERVER}/cspace-services{uri}'
        r = requests.get(url, auth=credentials)
        if r.status_code != 200:
            logging.info(f'status code for Object GET is {r.status_code}, not 200. skipping url is {url}')
            break
        try:
            cspaceObject = ET.XML(r.text.encode('utf-8'))
            original_xml = r.text

        except:
            logging.info(f'could not parse response for {url}')
            logging.info(f'uri is {uri}')
            continue

        content = {}
        for elem in cspaceObject.iter():
            if elem.text is not None:
                content[elem.tag] = elem.text

        has_dups = 0
        for (key,value) in FIELDS.items():
            elements = cspaceObject.findall(f'.//{key}')
            if len(elements) > 1:
                seen = []
                todelete = []
                for e in elements:
                    if e.text in seen:
                        FIELDS[key] += 1
                        has_dups += 1
                        logging.info(f'uri: {uri}: deleting {e.tag} {e.text}')
                        parent = e.getparent()
                        parent.remove(e)
                    else:
                        seen.append(e.text)

        if has_dups > 0:

            # keep the original record, just in case
            xml = open(f'{uri}.xml', 'w')
            xml.write(original_xml)
            xml.close()

            xml_string = ET.tostring(cspaceObject).decode('utf-8')

            url = f'{SERVER}/cspace-services{uri}?impTimeout=900'
            headers = {'Content-Type': 'application/xml'}
            r = requests.put(url, data=xml_string, headers=headers, auth=credentials)
            if r.status_code != 200:
                logging.info(f'status code for PUT is {r.status_code}, not 200. skipping. url is {url}')
                continue

        Row = [has_dups]
        for f in 'csid objectNumber title updatedAt'.split(' '):
            try:
                field = list_item.find(f'.//{f}').text
            except:
                field = ''
            Row.append(field)
