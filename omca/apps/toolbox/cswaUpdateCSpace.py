#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import json
import codecs
import time
import datetime
import csv
import sys

# from dirq.QueueSimple import QueueSimple

from toolbox.cswaHelpers import *
from toolbox.cswaConstants import OMCADATA
from common import cspace
from common.utils import deURN

from cspace_django_site.main import cspace_django_site

MAINCONFIG = cspace_django_site.getConfig()

# DIRQ = QueueSimple('/tmp/cswa')

MAXLOCATIONS = 1000

import xml.etree.ElementTree as etree

def getWhen2Post(config):

    try:
        when2post = config.get('info', 'when2post')
    except:
        # default is update immediately
        when2post = 'update'

    return when2post

def add2queue(requestType, uri, fieldset, updateItems, form):
    userdata = form['userdata']
    element = json.dumps((requestType, uri, userdata.username, userdata.cspace_password, fieldset, updateItems))
    # DIRQ.add(element)
    return ''


def updateCspace(fieldset, updateItems, form, config):
    uri = 'collectionobjects' + '/' + updateItems['objectCsid']
    when2post = getWhen2Post(config)
    writeLog(updateItems, uri, 'PUT', form, config)

    if when2post == 'update':
        # get the XML for this object
        connection = cspace.connection.create_connection(MAINCONFIG, form['userdata'])
        url = "cspace-services/" + uri
        try:
            url2, content, httpcode, elapsedtime = connection.make_get_request(url)
        except:
            sys.stderr.write("ERROR: problem GETting XML for %s\n" % url)
            raise
        if httpcode != 200:
            sys.stderr.write("ERROR: HTTP response code %s for GET %s\n" % (httpcode, url))
            sys.stderr.write("ERROR: content for %s: \n%s\n" % (url, content))
            return when2post, "ERROR: HTTP response code %s for GET %s\n" % (httpcode, url)
        if content is None:
            sys.stderr.write("ERROR: No XML returned from CSpace server for %s\n" % url)
            return when2post, "ERROR: No XML returned from CSpace server for %s\n" % url
        try:
            message, payload = updateXML(fieldset, updateItems, content)
        except:
            raise
            sys.stderr.write("ERROR generating update XML for fieldset %s\n" % fieldset)
            try:
                sys.stderr.write("ERROR: payload for PUT %s: \n%s\n" % (url, content))
            except:
                sys.stderr.write("ERROR: could not write 'content' to error log for %s: \n" % url)
            return when2post, "ERROR generating update XML for fieldset %s\n" % fieldset
        try:
            (url3, data, httpcode, elapsedtime) = postxml('PUT', uri, payload, form)
        except:
            sys.stderr.write("ERROR: failed PUT payload for %s: \n%s\n" % (url, payload))
            return when2post, "ERROR: failed PUT payload for %s: \n%s\n" % (url, payload)
        if data is None:
            sys.stderr.write("ERROR: failed PUT payload for %s: \n%s\n" % (url, payload))
            sys.stderr.write("ERROR: HTTP response code %s for  %s\n" % (httpcode, url))
            return when2post, "ERROR: Bad HTTP response code %s for  %s\n" % (httpcode, url)
        # sys.stderr.write("payload for %s: \n%s" % (url, payload))
        # sys.stderr.write("updated object with csid %s to REST API...\n" % updateItems['objectCsid'])
        return when2post, message
    elif when2post == 'queue':
        message = add2queue("PUT", uri, fieldset, updateItems, form)
        return when2post, message
    else:
        return 'invalid move action' % when2post, ''


def createObject(objectinfo, config, form):
    uri = 'collectionobjects'
    when2post = getWhen2Post(config)
    writeLog(objectinfo, uri, 'POST', form, config)

    if when2post == 'update':
        payload = createObjectXML(objectinfo)
        (url, data, csid, elapsedtime) = postxml('POST', uri, payload, form)
        return 'created new object', csid
    elif when2post == 'queue':
        add2queue("POST", uri, 'createobject', objectinfo, form)
        return 'queued new object', ''
    else:
        return 'invalid move action' % when2post, ''


def updateLocations(updateItems, config, form):
    uri = 'movements'
    when2post = getWhen2Post(config)
    writeLog(updateItems, uri, 'POST', form, config)

    if when2post == 'update':
        makeMH2R(updateItems, config, form)
        return 'moved', ''
    elif when2post == 'queue':
        add2queue("POST", uri, 'movements', updateItems, form)
        return 'queued move', ''
    else:
        return 'invalid move action' % when2post, ''


def IsAlreadyPreferred(txt, elements):
    if elements == []: return False
    if type(elements) == type([]):
        if txt == str(elements[0].text):
            #print "    found,skipping: ",txt
            return True
        return False
    # if we were passed in a single (non-array) Element, just check it..
    if txt == str(elements.text):
        #print "    found,skipping: ",txt
        return True
    return False


def alreadyExists(txt, elements):
    if elements == []: return False
    if type(elements) == type([]):
        for e in elements:
            #element = element[0]
            if txt == str(e.text):
                #print "    found,skipping: ",txt
                return True
        return False
    # if we were passed in a single (non-array) Element, just check it..
    if txt == str(elements.text):
        #print "    found,skipping: ",txt
        return True
    return False


def updateXML(fieldset, updateItems, xml):
    message = ''

    # omca labels
    for f in OMCADATA.keys():
        if fieldset == f:
            fieldList = []
            for x in OMCADATA[f]:
                if 'Museum #' in x[0]: continue
                fieldList.append(x[1])


    root = etree.fromstring(xml)
    # add the user's changes to the XML
    for relationType in fieldList:
        #sys.stderr.write('updating: %s = %s\n' % (relationType, updateItems[relationType]))
        # this app does not insert empty values into anything!
        if not relationType in updateItems.keys() or updateItems[relationType] == '':
            continue
        listSuffix = 'List'
        extra = ''
        if relationType in ['assocPeople', 'material', 'technique', 'objectProductionPerson', 'objectProductionOrganization', 'objectProductionDate', 'determinationHistory']:
            extra = 'Group'
        elif relationType in ['briefDescription', 'fieldCollector', 'responsibleDepartment', 'photo']:
            listSuffix = 's'
        elif relationType in ['collection', 'pahmaFieldLocVerbatim', 'ipAudit', 'doNotPublishOnWeb', 'argusDescription', 'fieldCollectionPlace', 'fieldCollectionDateGroup', 'copyrightHolder']:
            listSuffix = ''
        else:
            pass
        metadata = root.findall('.//' + relationType + extra + listSuffix)
        try:
            metadata = metadata[0] # there had better be only one!
        except:
            pass
            # hmmm ... we didn't find this element in the record. Make a note a carry on!
            # message += 'No "' + relationType + extra + listSuffix + '" element found to update.'
            #sys.stderr.write('did not find: %s\n' % (relationType + extra + listSuffix))
        #print(etree.tostring(metadata))
        #print ">>> ",relationType,':',updateItems[relationType]
        if relationType in 'assocPeople objectName material taxon technique objectProductionPerson objectProductionPlace'.split(' '):
            Entry = metadata.find('.//' + relationType)
            if Entry is not None:
                Entry.text = updateItems[relationType]
            else:
                new_group = etree.Element(relationType + 'Group')
                new_element = etree.Element(relationType)
                new_element.text = updateItems[relationType]
                new_group.insert(0,new_element)
                metadata.insert(0, new_group)
        elif relationType == 'determinationHistory':
            sys.stderr.write('starting dhName \n')
            Entry = metadata.find('.//dhName')
            if Entry is not None:
                Entry.text = updateItems[relationType]
            else:
                new_list = etree.Element(relationType + 'GroupList')
                new_group = etree.Element(relationType + 'Group')
                new_element = etree.Element('dhName')
                new_element.text = updateItems[relationType]
                new_list.insert(0,new_group)
                new_group.insert(0,new_element)
                schema = '{http://collectionspace.org/services/collectionobject/local/omca}collectionobjects_omca'
                collectionobjects_schema = root.find('.//%s' % schema)
                collectionobjects_schema.append(new_list)
        elif relationType == 'fieldCollectionDateGroup':
            # fieldCollectionDateGroup must be replaced completely...
            #sys.stderr.write("replacing %s in %s.\n" % (updateItems[relationType], relationType))
            for c in metadata:
                c.text = ''
                if c.tag == 'dateDisplayDate':
                    c.text = updateItems[relationType]
             #sys.stderr.write(etree.tostring(metadata) + '\n')

        # handle dates, they are special
        elif 'Date' in relationType:
            #sys.stderr.write("checking for value %s in %s.\n" % (updateItems[relationType], relationType))
            Entries = metadata.findall('.//dateDisplayDate')
            alreadyexists = False
            for child in Entries:
                #sys.stderr.write(' c: %s = %s\n' % (child.tag, child.text))
                if child.text == updateItems[relationType]:
                    alreadyexists = True
            if not alreadyexists:
                Entries[0].text = updateItems[relationType]
            else:
                message += "%s already exists in %s, not updated.<br/>" % (updateItems[relationType], relationType)

        elif relationType in 'ipAudit doNotPublishOnWeb argusDescription copyrightHolder fieldCollectionPlace'.split(' '):
            #sys.stderr.write("handling %s \n" % relationType)
            element = relationType
            if element in updateItems:
                e = root.find('.//%s' % element)
                if e is None:
                    e = etree.Element(element)
                    e.text = updateItems[element]
                    schema = '{http://collectionspace.org/services/collectionobject/local/omca}collectionobjects_omca'
                    if relationType == 'fieldCollectionPlace':
                        schema = '{http://collectionspace.org/services/collectionobject}collectionobjects_common'
                    collectionobjects_schema = root.find('.//%s' % schema)
                    collectionobjects_schema.append(e)
                    #message += "&lt;%s&gt; not found, created new one<br/>" % element
                    #sys.stderr.write("%s not found, created new one\n" % element)
                else:
                    #message += "'%s' added as &lt;%s&gt;.<br/>" % (updateItems[element], element)
                    e.text = updateItems[element]
                    #message += "'%s' updated as &lt;%s&gt;.<br/>" % (updateItems[element], element)
                    #sys.stderr.write('updated ' + etree.tostring(e) + "\n")

        else:
            # check if value is already present. if so, skip
            if alreadyExists(updateItems[relationType], metadata.findall('.//' + relationType)):
                if IsAlreadyPreferred(updateItems[relationType], metadata.findall('.//' + relationType)):
                    continue
            Entry = metadata.findall('.//' + relationType)
            Entry[0].text = updateItems[relationType]
            # sys.stderr.write(etree.tostring(metadata).decode('utf-8'))
            # sys.stderr.write(f'{relationType} = {updateItems[relationType]}')

    payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(root, encoding='unicode')
    # update collectionobject..
    # html += "<br>pretending to post update to %s to REST API..." % updateItems['objectCsid']
    # elapsedtimetotal = time.time()
    # messages = []
    # messages.append("posting to %s REST API..." % uri)
    # print(payload)
    # messages.append(payload)

    return message, payload


def createObjectXML(objectinfo):

    # get the XML for this object
    # get the XML for this object
    content = '''<document name="collectionobjects">
<ns2:collectionobjects_common xmlns:ns2="http://collectionspace.org/services/collectionobject" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<objectNameList>
<objectNameGroup>
<objectName/>
</objectNameGroup>
</objectNameList>
<objectNumber/>
</ns2:collectionobjects_common>
<ns2:collectionobjects_omca xmlns:ns2="http://collectionspace.org/services/collectionobject/local/omca" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<sortableObjectNumber/>
</ns2:collectionobjects_omca>
</document>'''

    root = etree.fromstring(content)
    for elementname in objectinfo:
        if elementname in objectinfo:
            element = root.find('.//' + elementname)
            element.text = str(objectinfo[elementname])

    payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(root, encoding='unicode')

    return payload


def makeMH2R(updateItems, config, form):
    institution = config.get('info', 'institution')

    try:
        uri = 'movements'

        # html += "<br>posting to movements REST API..."
        payload = lmiPayload(updateItems, institution)
        (url, data, movementcsid, elapsedtime) = postxml('POST', uri, payload, form)
        updateItems['subjectCsid'] = movementcsid

        uri = 'relations'

        # html += "<br>posting inv2obj to relations REST API..."
        updateItems['subjectDocumentType'] = 'Movement'
        updateItems['objectDocumentType'] = 'CollectionObject'
        payload = relationsPayload(updateItems)
        (url, data, ignorecsid, elapsedtime) = postxml('POST', uri, payload, form)

        # reverse the roles
        # html += "<br>posting obj2inv to relations REST API..."
        temp = updateItems['objectCsid']
        updateItems['objectCsid'] = updateItems['subjectCsid']
        updateItems['subjectCsid'] = temp
        updateItems['subjectDocumentType'] = 'CollectionObject'
        updateItems['objectDocumentType'] = 'Movement'
        payload = relationsPayload(updateItems)
        (url, data, ignorecsid, elapsedtime) = postxml('POST', uri, payload, form)

        writeLog(updateItems, uri, 'POST', form, config)

        # html += "<h3>Done w update!</h3>"
    except Exception as e:
        print(e[0])
        raise


def postxml(requestType, uri, payload, form):
    connection = cspace.connection.create_connection(MAINCONFIG, form['userdata'])
    return connection.postxml(uri="cspace-services/" + uri, payload=payload, requesttype=requestType)


def writeLog(updateItems, uri, httpAction, form, config):
    auditFile = config.get('files', 'auditfile')
    # TODO: unsnarl this someday. there should be only one way to specify which tool is in use.
    # TODO: and only one place all the logging should go (I think: not sure about audit trail...)
    try:
        updateType = form['tool']
    except:
        updateType = updateItems['updateType']
    try:
        username = form['userdata']
        username = username.username
    except:
        username = ''
    try:
        csvlogfh = csv.writer(codecs.open(auditFile, 'a', 'utf-8'), delimiter="\t")
        logrec = [httpAction, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), updateType, uri, username]
        for item in updateItems.keys():
            logrec.append("%s=%s" % (item, updateItems[item].replace('\n', '#')))
        csvlogfh.writerow(logrec)
    except:
        raise
        # html += 'writing to log %s failed!' % auditFile
        pass

