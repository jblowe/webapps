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
    print("finds all duplicated values in collection objects")
    print("outputs a list of records updated")
    print("")
    print("usage: python %s <config.cfg> <outputfile.csv> <startpage> <pagestoproc>" % sys.argv[0])
    print("")
    print("e.g:   nohup time python %s extract.cfg outputfile.csv 2 &" % sys.argv[0])
    print("")
    exit(1)

RECORD = 'collectionobjects'
CONFIG_FILE = sys.argv[1]
CSV_FILE = sys.argv[2]
START = int(sys.argv[3])
PAGES_TO_PROCESS = int(sys.argv[4])
PAGESIZE = 500
PAGES_RETRIEVED = 0
TOTAL_UPDATED = 0
TOTAL_PROCESSED = 0

FIELDS = {
    'color': 0,
    'dhName': 0,
    'fieldCollector': 0,
    'material': 0,
    'objectName': 0,
    'objectProductionDate': 0,
    'objectProductionOrganization': 0,
    'objectProductionPerson': 0,
    'photo': 0,
    'technique': 0
}

# don't need to check these, they are single-valued fields
# 'copyrightHolder': 0,
# 'fieldCollectionDate': 0,
# 'fieldCollectionPlace': 0,
# 'argusDescription': 0,
# 'doNotPublishOnWeb': 0,
# 'ipAudit': 0,

with open(CONFIG_FILE, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        SERVER = config['SERVER']
        CREDS = config['CREDS']
        credentials = tuple(CREDS.split(':'))
    except yaml.YAMLError as exc:
        logging.info(exc)

cspaceCSV = csv.writer(codecs.open(CSV_FILE, 'w', "utf-8"), delimiter='\t')

while True:
    try:

        # retrieve the 1st page of records each time, until we get a page with no items...
        logging.info(f'retrieving page {PAGES_RETRIEVED + START}')
        url = f'{SERVER}/cspace-services/{RECORD}?pgSz={PAGESIZE}&pgNum={PAGES_RETRIEVED + START}'
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
        itemsInPage = int(cspaceXML.find('.//itemsInPage').text)
        logging.info(f'page {PAGES_RETRIEVED + START} retrieved, {itemsInPage} items')
        if itemsInPage == 0:
            logging.info(f'nothing left to do, leaving infinite loop')
            break
        items = cspaceXML.findall('.//list-item')

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
                            if 'Group' in parent.tag:
                                e = parent
                                parent = e.getparent()
                            parent.remove(e)
                        else:
                            seen.append(e.text)

            if has_dups > 0:

                # keep the original record, just in case
                xml = open(f'.{uri}.xml', 'w')
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
            cspaceCSV.writerow(Row)
            if has_dups > 0:
                number_updated += 1

        logging.info(f'update {number_updated} of {itemsInPage}')
        TOTAL_PROCESSED += itemsInPage
        TOTAL_UPDATED += number_updated
        PAGES_RETRIEVED += 1
        if PAGES_TO_PROCESS == PAGES_RETRIEVED:
            break
    except:
        logging.info(f'error retrieving or parsing or updating the XML for {url}')
        raise

logging.info(f'PAGES_RETRIEVED: {PAGES_RETRIEVED}')
logging.info(f'TOTAL_PROCESSED: {TOTAL_PROCESSED}')
logging.info(f'TOTAL_UPDATED:   {TOTAL_UPDATED}')
