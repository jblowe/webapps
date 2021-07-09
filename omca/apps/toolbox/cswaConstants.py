#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import csv, sys, time, os, datetime
import configparser
from os import path

SITE_ROOT = path.dirname(path.realpath(__file__))

OMCADATA = {
    'mattech': [('Museum #', 'objnum', 'onn', 2, '', ''),
                ('Object name', 'objectName', 'on', 1, 'concept', 'concepts_common'),
                ('Material', 'material', 'ma', 11, 'concept', 'concepts_common'),
                ('Technique', 'technique', 'tnq', 21, '', ''),
                ('Material/Technique Summary', 'argusDescription', 'ard', 9, 'argusDescription', '')],
    'nameprod': [('Museum #', 'objnum', 'onn', 2, '', ''),
                 ('Object name', 'objectName', 'on', 1, 'concept', 'concepts_common'),
                 ('Production Person', 'objectProductionPerson', 'pc', 12, 'person', 'persons_common'),
                 ('Production Organization', 'objectProductionOrganization', 'or', 13, 'organization', 'organizations_common'),
                 ('Production Date', 'objectProductionDate', 'pdt', 15, '', '')],
    'specimen': [('Museum #', 'objnum', 'onn', 2, 'concept', 'concepts_common'),
                 ('DH name', 'determinationHistory', 'ta', 10, 'taxon', 'taxon_common'),
                 ('Field collection date', 'fieldCollectionDateGroup', 'cod', 4, '', ''),
                 ('Field collection place', 'fieldCollectionPlace', 'px', 3, 'place', 'places_common'),
                 ('Field collector', 'fieldCollector', 'pc', 5, 'collectionobjects_common_fieldcollectors', '')],
    'rights': [('Museum #', 'objnum', 'onn', 2, '', ''),
               ('Object name', 'objectName', 'on', 1, 'concept', 'concepts_common'),
               ('IP Audit', 'ipAudit', 'ipa', 18, 'item', ''),
               ('Do not publish on web', 'doNotPublishOnWeb', 'dnp', 16, '', ''),
               ('Copyright Holder', 'copyrightHolder', 'pc', 20, 'person', 'persons_common'),
               ('Photo', 'photo', 'pho', 19, '', '')]
}

def getStyle(schemacolor1):
    return '''
<style type="text/css">
body { margin:10px 10px 0px 10px; font-family: Arial, Helvetica, sans-serif; }
table { }
td { padding-right: 10px; }
th { text-align: left ;color: #666666; font-size: 16px; font-weight: bold; padding-right: 20px;}
h2 { font-size:32px; padding:10px; margin:0px; border-bottom: none; }
h3 { font-size:24px; padding:10px; }
p { padding:10px 10px 10px 10px; }
li { text-align: left; list-style-type: none; }
a { text-decoration: none; }
button { font-size: 150%; width:85px; text-align: center; text-transform: uppercase;}
.monty { }
.cell { line-height: 1.0; text-indent: 2px; color: #666666; font-size: 16px;}
.enumerate { background-color: green; font-size:20px; color: #FFFFFF; font-weight:bold; vertical-align: middle; text-align: center; }
img#logo { float:left; height:50px; padding:10px 10px 10px 10px;}
.authority { color: #000000; background-color: #FFFFFF; font-weight: bold; font-size: 18px; }
.ncell { line-height: 1.0; cell-padding: 2px; font-size: 16px;}
.zcell { min-width:80px; cell-padding: 2px; font-size: 16px;}
.shortcell { width:180px; cell-padding: 2px; font-size: 16px;}
.objname { font-weight: bold; font-size: 16px; font-style: italic; min-width:200px; }
.objno { font-weight: bold; font-size: 16px; font-style: italic; }
.ui-tabs .ui-tabs-panel { padding: 0px; min-height:120px; }
.rdo { text-align: center; width:60px; }
.error {color:red;}
.warning {color:chocolate;}
.ok {color:green;}
.save { background-color: BurlyWood; font-size:20px; color: #000000; font-weight:bold; vertical-align: middle; text-align: center; }
.shortinput { font-weight: bold; width:150px; }
.subheader { background-color: ''' + schemacolor1 + '''; color: #FFFFFF; font-size: 24px; font-weight: bold; }
.smallheader { background-color: ''' + schemacolor1 + '''; color: #FFFFFF; font-size: 12px; font-weight: bold; }
.veryshortinput { width:60px; }
.xspan { color: #000000; background-color: #FFFFFF; font-weight: bold; font-size: 12px; }
th[data-sort]{ cursor:pointer; }
.littlebutton {color: #FFFFFF; background-color: gray; font-size: 11px; padding: 2px; cursor: pointer; }
.imagecell { padding: 8px ; align: center; }
.rightlabel { text-align: right ; vertical-align: top; padding: 2px 12px 2px 2px; width: 30%; }
.objtitle { font-size:28px; float:left; padding:4px; margin:0px; border-bottom: thin dotted #aaaaaa; color: #000000; }
.objsubtitle { font-size:28px; float:left; padding:2px; margin:0px; border-bottom: thin dotted #aaaaaa; font-style: italic; color: #999999; }
.notentered { font-style: italic; color: #999999; }
</style>
'''


def infoHeaders(fieldSet):
    # omca labels
    for f in OMCADATA.keys():
        if fieldSet == f:
            header = '<table><tr>'
            for x in OMCADATA[f]: header += '<th>%s</th>' % x[0]
            header += '</tr>'
            return header


def ipAuditValues():
    return [
        ("Assumed Protected by Copyright", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(assumed_protected_by_copyright)'Assumed Protected by Copyright'"),
        ("Copyright OMCA", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(copyright_omca)'Copyright OMCA'"),
        ("No Known Restrictions", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(no_known_restrictions)'No Known Restrictions'"),
        ("OMCA Licensed", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(omca_licensed)'OMCA Licensed'"),
        ("Protected by Copyright", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(protected_by_copyright)'Protected by Copyright'"),
        ("Public Domain", "urn:cspace:museumca.org:vocabularies:name(ipaudit):item:name(public_domain)'Public Domain'")
    ]


def getDropdown(listname, csid, dropdownlist, selected):
    dropdown = '''
          <select class="cell" name="%s.%s">
              <option value="None">Select a value</option>''' % (listname, csid)
    for dd in dropdownlist:
        # print dd
        dropdownOption = """<option value="%s">%s</option>""" % (dd[1], dd[0])
        # sys.stderr.write('v=%s t=%s s=%s \n' % (dd[1],dd[0],selected))
        if str(selected) in dd[1] and selected != '':
            dropdownOption = dropdownOption.replace('option ', 'option selected ')
            sys.stderr.write(dropdownOption + '\n')
        dropdown += dropdownOption

    dropdown += '\n      </select>'
    return dropdown


def getHandlers(form, institution):
    selected = form.get('handlerRefName')

    handlerlist = [
        ("Anna Bunting", "urn:cspace:museumca.org:personauthorities:name(person):item:name(AnnaBunting1457972526862)'Anna Bunting'"),
        ("Christine Osborne", "urn:cspace:museumca.org:personauthorities:name(person):item:name(staff1986)'Christine Osborne'"),
        ("Jadeen Young", "urn:cspace:museumca.org:personauthorities:name(person):item:name(staff1977)'Jadeen Young'"),
        ("Meredith Patute", "urn:cspace:museumca.org:personauthorities:name(person):item:name(staff1968)'Meredith Patute'"),
        ("Nathan Kerr", "urn:cspace:museumca.org:personauthorities:name(person):item:name(staff1933)'Nathan Kerr'"),
        ("Valerie Huaco", "urn:cspace:museumca.org:personauthorities:name(person):item:name(staff1941)'Valerie Huaco'"),
        ("Violetta Wolf", "urn:cspace:museumca.org:personauthorities:name(person):item:name(ViolettaWolf1479834146619)'Violetta Wolf'"),
        ("Jenny Heffernon", "urn:cspace:museumca.org:personauthorities:name(person):item:name(JennyHeffernon1574348180495)'Jenny Heffernon'"),
        ("Ellis Martin", "urn:cspace:museumca.org:personauthorities:name(person):item:name(EllisMartin1563380476380)'Ellis Martin'"),
        ("Natalie Wiener", "urn:cspace:museumca.org:personauthorities:name(person):item:name(NatalieWiener1497043697832)'Natalie Wiener'")
    ]

    handlers = '''
          <select class="cell" name="handlerRefName">
              <option value="None">Select a handler</option>'''

    for handler in handlerlist:
        #print(handler)
        handlerOption = """<option value="%s">%s</option>""" % (handler[1], handler[0])
        #print("xxxx",selected)
        if selected and str(selected) == handler[1]:
            handlerOption = handlerOption.replace('option', 'option selected')
        handlers = handlers + handlerOption

    handlers += '\n      </select>'
    return handlers, selected


def getReasons(form, institution):
    reason = form.get('reason')

    dropdownlist = [
        ("Conservation", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(conservation)'Conservation'"),
        ("Exhibition", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(exhibition)'Exhibition'"),
        ("Inventory", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(inventory)'Inventory'"),
        ("Loan", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(loan)'Loan'"),
        ("New Storage Location", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(new_storage_location)'New Storage Location'"),
        ("Photography", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(photography)'Photography'"),
        ("Research", "urn:cspace:museumca.org:vocabularies:name(reasonformove):item:name(research)'Research'")
    ]

    dropdown = '''
          <select class="cell" name="reason">
              <option value="None">Select a value</option>'''
    for dd in dropdownlist:
        # print dd
        dropdownOption = """<option value="%s">%s</option>""" % (dd[1], dd[0])
        dropdown += dropdownOption
    dropdown += '\n      </select>'
    reasons = dropdown

    reasons = reasons.replace(('option value="%s"' % reason), ('option selected value="%s"' % reason))
    return reasons, reason


def getLegacyDepts(form, csid, ld):
    selected = form.get('legacydept')

    legacydeptlist = []

    legacydepts = \
          '''<select class="cell" name="ld.''' + csid + '''">
              <option value="None">Select a legacy department</option>'''

    for legacydept in legacydeptlist:
        if legacydept[1] == ld:
            legacydeptOption = """<option value="%s" selected>%s</option>""" % (legacydept[1], legacydept[0])
        else:
            legacydeptOption = """<option value="%s">%s</option>""" % (legacydept[1], legacydept[0])
        legacydepts = legacydepts + legacydeptOption

    legacydepts += '\n      </select>'
    return legacydepts, selected


def selectWebapp(form, webappconfig):

    if form.get('webapp') == 'switchapp':
        #sys.stderr.write('%-13s:: %s' % ('switchapp','looking for creds..'))
        username = form.get('csusername')
        password = form.get('cspassword')
        payload = '''
            <input type="hidden" name="checkauth" value="true">
            <input type="hidden" name="csusername" value="%s">
            <input type="hidden" name="cspassword" value="%s">''' % (username, password)
    else:
        payload = ''


    programName = ''
    apptitles = {}
    serverlabels = {}
    badconfigfiles = ''


    tools = webappconfig.get('tools','availabletools')
    tools = tools.replace('\n','').split(',')
    for tool in tools:
        if tool == 'landing':
            continue
        try:
            # check to see that all the needed values are available...
            logo = webappconfig.get('info','logo')
            schemacolor1 = webappconfig.get('info','schemacolor1')
            institution = webappconfig.get('info','institution')
            serverlabel = webappconfig.get('info','serverlabel')

            apptitle = webappconfig.get(tool,'apptitle')
            updateactionlabel = webappconfig.get(tool,'updateactionlabel')
            updateType = webappconfig.get(tool,'updatetype')
            apptitles[apptitle] = updateType
        except:
            badconfigfiles += '<tr><td>%s</td></tr>' % tool

    line = '<table>\n'

    for apptitle in sorted(apptitles.keys()):
            line += '<tr><td><a href="%s">%s</a></td></tr>\n' % (apptitles[apptitle], apptitle)

    if badconfigfiles != '':
        line += '<tr><td colspan="2"><h2>%s</h2></td></tr>' % 'bad config files'
        line += badconfigfiles

    line += '</table>\n'

    return line


def getPrinters(form):
    selected = form.get('printer')

    printerlist = [
        ("Kroeber Hall", "cluster1"),
        ("Regatta", "cluster2")
    ]

    printers = '''
          <select class="cell" name="printer">
              <option value="None">Select a printer</option>'''

    for printer in printerlist:
        printerOption = """<option value="%s">%s</option>""" % (printer[1], printer[0])
        if selected and str(selected) == printer[1]:
            printerOption = printerOption.replace('option', 'option selected')
        printers += printerOption

    printers += '\n      </select>'
    return printers, selected, printerlist


def getFieldset(form, institution):
    selected = form.get('fieldset')


    fields = [
        ("Material & Technique", "mattech"),
        ("Name & Production", "nameprod"),
        ("Specimen Information", "specimen"),
        ("Rights", "rights"),
        ]


    fieldset = '''
          <select class="cell" name="fieldset">'''

    for field in fields:
        fieldsetOption = """<option value="%s">%s</option>""" % (field[1], field[0])
        if selected and str(selected) == field[1]:
            fieldsetOption = fieldsetOption.replace('option', 'option selected')
        fieldset += fieldsetOption

    fieldset += '\n      </select>'
    return fieldset, selected


def getHierarchies(form, known_authorities):
    selected = form.get('authority')

    # this is a list of all the authorities the viewer knows how to handle.
    # the list of authorities for an institution is a parm in the .cfg file for
    # the hierarchy viewer and is passed in as 'authorities'
    authoritylist = [
        ("Concept", "concept"),
        ("Place", "place"),
        ("Organization", "organization"),
        ("Taxon", "taxonomy"),
        # ("Storage Location", "location"),
    ]

    authorities = '''
    <select class="cell" name="authority">
    <option value="None">Select an authority</option>'''

    # sys.stderr.write('selected %s\n' % selected)
    for authority in authoritylist:
        authorityOption = """<option value="%s">%s</option>""" % (authority[1], authority[0])
        # sys.stderr.write('check hierarchy %s %s\n' % (authority[1], authority[0]))
        if selected == authority[1]:
            # sys.stderr.write('found hierarchy %s %s\n' % (authority[1], authority[0]))
            authorityOption = authorityOption.replace('option', 'option selected')
        authorities = authorities + authorityOption

    authorities += '\n </select>'
    return authorities, selected


def getAltNumTypes(form, csid, ant):
    selected = form.get('altnumtype')

    altnumtypelist = []

    altnumtypes = '''<select class="cell" name="ant.''' + csid + '''">
              <option value="None">Select a number type</option>'''

    for altnumtype in altnumtypelist:
        if altnumtype[0] == ant:
            altnumtypeOption = """<option value="%s" selected>%s</option>""" % (altnumtype[0], altnumtype[1])
        else:
            altnumtypeOption = """<option value="%s">%s</option>""" % (altnumtype[0], altnumtype[1])
        altnumtypes = altnumtypes + altnumtypeOption

    altnumtypes += '\n      </select>'
    return altnumtypes, selected


def getObjectStatuses(form, csid, ant):
    selected = form.get('objectstatus')

    objectstatuslist = []

    objectstatuses = '''<select class="cell" name="obs.''' + csid + '''">
        <option value="None">Select an object status</option>'''

    for objectstatus in objectstatuslist:
        if objectstatus[0] == ant:
            objectstatusOption = """<option value="%s" selected>%s</option>""" % (objectstatus[0], objectstatus[1])
        else:
            objectstatusOption = """<option value="%s">%s</option>""" % (objectstatus[0], objectstatus[1])
        objectstatuses = objectstatuses + objectstatusOption

    objectstatuses += '\n      </select>'
    return objectstatuses, selected


def getObjType(form, csid, ot):
    selected = form.get('objectType')

    objtypelist = []

    objtypes = \
          '''<select class="cell" name="ot.''' + csid + '''">
              <option value="None">Select an object type</option>'''

    for objtype in objtypelist:
        if objtype[1] == ot:
            objtypeOption = """<option value="%s" selected>%s</option>""" % (objtype[1], objtype[0])
        else:
            objtypeOption = """<option value="%s">%s</option>""" % (objtype[1], objtype[0])
        objtypes = objtypes + objtypeOption

    objtypes += '\n      </select>'
    return objtypes, selected


def getCollMan(form, csid, cm):
    selected = form.get('collMan')

    collmanlist = []

    collmans = \
          '''<select class="cell" name="cm.''' + csid + '''">
              <option value="None">Select a collection manager</option>'''

    for collman in collmanlist:
        if collman[1] == cm:
            collmanOption = """<option value="%s" selected>%s</option>""" % (collman[1], collman[0])
        else:
            collmanOption = """<option value="%s">%s</option>""" % (collman[1], collman[0])
        collmans = collmans + collmanOption

    collmans += '\n      </select>'
    return collmans, selected


def getAgencies(form):
    selected = form.get('agency')

    agencylist = []

    agencies = '''
<select class="cell" name="agency">
<option value="None">Select an agency</option>'''

    for agency in agencylist:
        agencyOption = """<option value="%s">%s</option>""" % (agency[1], agency[0])
        if selected == agency[1]:
            agencyOption = agencyOption.replace('option', 'option selected')
        agencies += agencyOption

    agencies += '\n </select>'
    return agencies, selected

def getIntakeFields(fieldset):

    if fieldset == 'intake':

        return [
            ('TR', 20, 'tr','31','fixed'),
            ('Number of Objects:', 5, 'numobjects','1','text'),
            ('Source:', 40, 'pc.source','','text'),
            ('Date in:', 30, 'datein',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'text'),
            ('Receipt?', 40, 'receipt','','checkbox'),
            ('Location:', 40, 'lo.location','','text'),
            ('Disposition:', 30, 'disposition','','text'),
            ('Artist/Title/Medium', 10, 'atm','','text'),
            ('Purpose:', 40, 'purpose','','text')
        ]
    elif fieldset == 'objects':

        return [
            ('ID number', 30, 'id','','text'),
            ('Title', 30, 'title','','text'),
            ('Comments', 30, 'comments','','text'),
            ('Artist', 30, 'pc.artist','','text'),
            ('Creation date', 30, 'cd','','text'),
            ('Creation technique', 30, 'ct','','text'),
            ('Dimensions', 30, 'dim','','text'),
            ('Responsible department', 30, 'rd','','text'),
            ('Computed current location', 30, 'lo.loc','','text')
            ]


def getHeader(updateType, institution):
    if updateType == 'inventory':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th>Found</th>
      <th style="width:60px; text-align:center;">Not Found</th>
      <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Found</th>
      <th style="width:60px; text-align:center;">Not Found</th>
      <th>Notes</th>
    </tr>"""
    elif updateType == 'movecrate':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move" checked/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move"/></th>
      <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move" checked/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move"/></th>
      <th>Notes</th>
    </tr>"""

    elif updateType == 'powermove':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move"/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move" checked/></th>
     <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move"/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move" checked/></th>
     <th>Notes</th>
    </tr>"""


    elif updateType == 'packinglist':

        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th style="width:150px;">Title</th>
      <th>Artist</th>
      <th>Medium</th>
      <th>Dimensions</th>
      <th>Credit Line</th>
    </tr>
        """
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Maker</th>
      <th>Material Summary</th>
      <th></th>
      <th></th>
    </tr>"""
    elif updateType == 'moveobject':
        return """
    <table><tr>
      <th>Move?</th>
      <th>Museum #</th>
      <th>Object name</th>
      <th></th>
      <th>Location</th>
    </tr>"""
    elif updateType == 'bedlist':
        return """
    <table class="tablesorter-blue" id="sortTable%s"><thead>
    <tr>
      <th data-sort="float">Accession</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Taxonomic Name</th>
      <th data-sort="string">Rare?</th>
      <th data-sort="string">Accession<br/>Dead?</th>
    </tr></thead><tbody>"""
    elif updateType == 'bedlistxxx' or updateType == 'advsearchxxx':
        return """
    <table class="tablesorter-blue" id="sortTable%s"><thead>
    <tr>
      <th data-sort="float">Accession Number</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Taxonomic Name</th>
    </tr></thead><tbody>"""
    elif updateType == 'bedlistnone':
        return """
    <table class="tablesorter-blue" id="sortTable"><thead><tr>
      <th data-sort="float">Accession</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Taxonomic Name</th>
      <th data-sort="string">Rare?</th>
      <th data-sort="string">Accession<br/>Dead?</th>
      <th>Garden Location</th>
    </tr></thead><tbody>"""
    elif updateType in ['locreport', 'holdings', 'advsearch']:
        return """
    <table class="tablesorter-blue" id="sortTable"><thead><tr>
      <th data-sort="float">Accession</th>
      <th data-sort="string">Taxonomic Name</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Garden Location</th>
      <th data-sort="string">Locality</th>
      <th data-sort="string">Rare?</th>
      <th data-sort="string">Accession<br/>Dead?</th>
    </tr></thead><tbody>"""
    elif updateType == 'keyinfoResult' or updateType == 'objinfoResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Status</th>
      <th>CSID</th>
    </tr>"""
    elif updateType == 'inventoryResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Updated Inventory Status</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'barcodeprint':
        return """
    <table width="100%"><tr>
      <th>Location</th>
      <th>Objects found</th>
      <th>Barcode Filename</th>
      <th>Notes</th>
    </tr>"""
    elif updateType == 'barcodeprintlocations':
        return """
    <table width="100%"><tr>
      <th>Locations listed</th>
      <th>Barcode Filename</th>
    </tr>"""
    elif updateType == 'upload':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'intakeValues':
        return """
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>"""
    elif updateType == 'intakeResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'intakeObjects':
        return """
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""


if __name__ == '__main__':

    def handleResult(result,header):
        header = '\n<tr><td>%s<td>' % header
        if type(result) == type(()) and len(result) >= 2:
            return header + result[0]
        elif type(result) == type('string'):
            return header + result
        else:
            print("handleResult error")
            #return result
            #return "\n<h2>some other result</h2>\n"

    form = {}
    config = {}

    result = '<html>\n'

    result += getStyle('blue')

    # all the following return HTML)
    result += '<h2>Dropdowns</h2><table border="1">'
    #result += handleResult(getAppOptions('pahma'),'getAppOptions')
    result += handleResult(getAltNumTypes(form, 'test-csid', 'attributed pahma number'),'getAltNumTypes')
    result += handleResult(getHandlers(form,'bampfa'),'getHandlers: bampfa')
    result += handleResult(getHandlers(form,''),'getHandlers')
    result += handleResult(getReasons(form,'bampfa'),'getReasons:bampfa')
    result += handleResult(getReasons(form,''),'getReasons')
    result += handleResult(getPrinters(form),'getPrinters')
    result += handleResult(getFieldset(form,'pahma'),'getFieldset')
    result += handleResult(getFieldset(form,'bampfa'),'getFieldset')
    result += handleResult(getHierarchies(form, ['']),'getHierarchies')
    result += handleResult(getAgencies(form),'getAgencies')
    result += '</table>'

    result += '<h2>Headers</h2>'
    for h in 'inventory movecrate packinglist packinglistbyculture moveobject bedlist bedlistnone keyinfoResult objinfoResult inventoryResult barcodeprint barcodeprintlocations upload'.split(' '):
        result += '<h3>Header for %s</h3>' % h
        header = getHeader(h,'')
        result += header.replace('<table', '<table border="1" ')
        result += '</table>'

    print('''Content-Type: text/html; charset=utf-8

    ''')
    print(result)


    result += '</html>\n'

