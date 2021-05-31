from lxml import etree as ET
import sys

cspaceXML = ET.parse(sys.argv[1])

try:
    permissions = cspaceXML.find('.//{http://collectionspace.org/services/authorization}account_permission')
    parent = permissions.getparent()
    parent.remove(permissions)
except:
    pass

# try:
#     core = cspaceXML.find('.//{http://collectionspace.org/collectionspace_core/}collectionspace_core')
#     parent = core.getparent()
#     parent.remove(core)
# except:
#     pass
 
xml_string = ET.tostring(cspaceXML).decode('utf-8')
xml = open(sys.argv[1], 'w')
xml.write(xml_string)
xml.close()
