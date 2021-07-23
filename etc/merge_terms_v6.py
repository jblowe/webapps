#!/usr/bin/env python3

# this version of the merge authorities script works with cspace v6.x
# (there is a small difference in the way that terms are searched in v6.x
# that is incompatible with earlier versions.)

import requests
import sys
import re

user = 'user@museumca.org'
pword = 'password'
baseurl = 'http://10.161.2.194/cspace-services'

headers = {'Content-Type': 'application/xml; charset=utf-8'}
urlparams = '/refObjs?pgSz=1000'
newcsid = sys.argv[2]
oldcsid = sys.argv[3]
to_update = []
vocabs = ['concept', 'org', 'location', 'place', 'person']
success = []
failed = []
relToDel = []
relSuccess = []
relFailed = []


# retrieve the refname for authority term
def getrefname(csid, vocab):
    url = baseurl + '/' + vocab + 'authorities/urn:cspace:name(' + vocab + ')/items/' + csid
    info = requests.get(url, headers=headers, auth=(user, pword))
    refname = re.search('<refName>(.*?)</refName>', info.text)
    try:
        return(refname.group(1))
    except:
        return None


# retrieve the uris of records that use the 'old term' and add them to a list
def getobjs(oldcsid):
    url = baseurl + '/' + termvocab + 'authorities/urn:cspace:name(' + termvocab + ')/items/' + oldcsid + urlparams
    usedby = requests.get(url, headers=headers, auth=(user, pword))
    if usedby.status_code != 200:
        print('Failed to find any related records.')
        return 0
    for match in re.findall('<uri>(.*?)</uri>', usedby.text):
        to_update.append(match)
        to_update.sort()
    count = re.search('<totalItems>(.*?)</totalItems>',
                      usedby.text, re.DOTALL).group(1)
    print('Found ' + count + ' records to be updated.')
    return(count)

# get a list of all the hierarchy rleationships that involve the oldterm
def getRels(csid):
    objRelations = requests.get(baseurl + '/relations?obj=' + csid,
                                headers=headers, auth=(user, pword))
    for match in re.findall('<relation-list-item><uri>(.*?)</uri>', objRelations.text):
        relToDel.append(match)
        relToDel.sort()
    
    subjRelations = requests.get(baseurl + '/relations?sbj=' + csid,
                                 headers=headers, auth=(user, pword))
    for sbjMatch in re.findall('<relation-list-item><uri>(.*?)</uri>', subjRelations.text):
        relToDel.append(sbjMatch)
        relToDel.sort()

# update list of records replacing 'old term' wth term being merged into and
# remove core and account info sections of the xml before uploading updated
# data and reading back a list of any failed attempts
def updateobjs(uri, oldrefname, newrefname):
    record = requests.get(baseurl + uri, headers=headers, auth=(user, pword))
    core = re.search('<ns2:collectionspace_core(.*?)</ns2:collectionspace'
                     '_core>', record.text, re.DOTALL)
    accnt = re.search('<ns2:account_permission(.*?)</ns2:account_permission>',
                      record.text, re.DOTALL)
    updated = record.text.replace(oldrefname, newrefname)
    for_upload = updated.replace(accnt.group(0), '').replace(core.group(0), '')
    update = requests.put(baseurl + uri, headers=headers,
                          data=for_upload.encode('utf-8'), auth=(user, pword))
    if update.status_code == 200:
        success.append(uri)
    else:
        failed.append(uri)


def delRels(uri):
    remove = requests.delete(baseurl + uri, auth=(user, pword))
    if remove.status_code == 200:
        relSuccess.append(uri)
    else:
        relFailed.append(uri)

# remove term that is no longer used
def deloldterm(csid, vocab):
    url = baseurl + '/' + vocab + 'authorities/urn:cspace:name(' + vocab + ')/items/' + csid
    remove = requests.delete(url, auth=(user, pword))
    return(remove.status_code)


# put all the functions together and execute
def mergeterms():
    oldrefname = getrefname(oldcsid, termvocab)
    newrefname = getrefname(newcsid, termvocab)
    getRels(oldcsid)
    countUsedby = getobjs(oldcsid)
    for uri in to_update:
        updateobjs(uri, oldrefname, newrefname)
    if len(failed) == 0:
        if int(countUsedby) == 0:
            print('No record relations found, none deleted.')
        elif int(countUsedby) < 1000:
            print('All record relations (if any!) were successfully deleted.')
        else:
            print(str(len(success)) + ' record relations successfully deleted.'
                  ' Re-run merge_terms to update remaining ' +
                  str(int(countUsedby) - len(success)) + ' records')
        status_code = deloldterm(oldcsid, termvocab)
        if status_code == 200:
            print(oldcsid + ' successfully deleted.')
        elif status_code == 404:
            print('Not found (already deleted?): ' + oldcsid)
        else:
            print('Error deleting term: ' + oldcsid)
    else:
        print(str(len(success)) + ' record relations were successfully updated.'
              + '\n the following records were not updated:')
        for item in failed:
            print(item)
    for csid in relToDel:
        delRels(csid)
    if len(relFailed) == 0:
        print('All hierarchy relationships (if any) were successfully deleted.')
    else:
        print('Error deleting the following hierarchy relationships: ' + ', '.join(relFailed))


# data validation for authority type
if sys.argv[1] not in vocabs:
    print('Invalid authority use one of the following:')
    for v in vocabs:
        print(v)
else:
    termvocab = sys.argv[1]
    if oldcsid == newcsid:
        print('Cannot merge ' + oldcsid + ' with ' + newcsid)
    else:
        mergeterms()
