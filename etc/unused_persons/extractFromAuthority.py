import xml.etree.ElementTree as ET
import sys, csv


if len(sys.argv) != 4:
    print("")
    print("reads a CSpace authority XML file and outputs CSIDs, displayNames, and refNames as a .csv file")
    print("")
    print("3rd argument says what type of extract to do: authority or items")
    print("")
    print("if duplicate displaynames are seen this are output to stdout")
    print("")
    print("usage: python %s <authorityfile.xml> <outputfile.csv> <authority|items> > listofdups.txt" % sys.argv[0])
    print("")
    print("e.g:   python %s organization.xml organization.csv items > listofdups.txt" % sys.argv[0])
    exit(1)

authority = 'csid termDisplayName refName updatedAt'.split(' ')
items = 'csid displayName uri updatedAt'.split(' ')

if sys.argv[3] == 'authority':
    fields_to_extract = authority
elif sys.argv[3] == 'items':
    fields_to_extract = items
else:
    print('3rd arg needs to be <authority|items>')
    sys.exit(1
             )

def extract_tag(xml, tag):
    element = xml.find('.//%s' % tag)
    return element.text


xData = []
try:
    cspaceXML = ET.parse(sys.argv[1])
    root = cspaceXML.getroot()
    items = cspaceXML.findall('.//list-item')
    for i in items:
        outputrow = []
        for f in fields_to_extract:
            e = i.find(f'.//{f}')
            if e is not None:
                outputrow.append(e.text)
            else:
                outputrow.append('')
        xData.append(outputrow)
    del items, root, cspaceXML
except:
    raise

cspaceCSV = csv.writer(open(sys.argv[2], 'w'), delimiter='\t')
entities = {}

numberofitems = len(xData)
# if numberofitems > numberWanted:
#    items = items[:numberWanted]

name_dict = {}
for sequence_number, i in enumerate(xData):
    [csid, Name, refName, updated_at] = i

    if Name in name_dict:
        print('%s\t%s\t%s' % (Name, csid, name_dict[Name]))
    else:
        name_dict[Name] = csid
    cspaceCSV.writerow([sequence_number, csid, Name, refName, updated_at])