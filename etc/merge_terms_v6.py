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
to_update = []
vocabs = ['citation', 'concept', 'org', 'location', 'place', 'person', 'taxon']
success = []
failed = []
relToDel = []
relSuccess = []
relFailed = []

# check arguments
if len(sys.argv) != 4:
    print('\nneed 3 arguments:\n')
    print(f'{sys.argv[0]} authority newcsid oldcsid')
    print('\ne.g.\n')
    print(f'{sys.argv[0]} org 7760fbb2-f8ff-400c-8e9c fd38782a-5680-4dbc-b786')
    print('')
    print('"authority" must be one of the following:\n')
    for v in vocabs:
        print(v)
    print('')
    sys.exit(1)

newcsid = sys.argv[2]
oldcsid = sys.argv[3]

# retrieve the refname for authority term
def getrefname(csid, vocab):
    if vocab == 'org':
        vocab2 = 'organization'
    else:
        vocab2 = vocab
    url = baseurl + '/' + vocab + 'authorities/urn:cspace:name(' + vocab2 + ')/items/' + csid
    info = requests.get(url, headers=headers, auth=(user, pword))
    if info.status_code != 200:
        print(f'Could not retrieve refname for {csid}. HTTP error response from CSpace server: {info.status_code}')
    refname = re.search('<refName>(.*?)</refName>', info.text)
    try:
        return(refname.group(1))
    except:
        return None

# check to see that a refname is really a refname
def checkrefname(refname, csid, which):
    if refname is None:
        print(f'\ncould not find refname for {which} {csid}')
        print('\nplease check the csid. cannot continue. sorry.\n')
        sys.exit(1)
    if 'urn' in refname:
        print(f'found refname {refname} for {which} {csid}')

# retrieve the uris of records that use the 'old term' and add them to a list
def getobjs(oldcsid):
    if termvocab == 'org':
        vocab2 = 'organization'
    else:
        vocab2 = termvocab
    url = baseurl + '/' + termvocab + 'authorities/urn:cspace:name(' + vocab2 + ')/items/' + oldcsid + urlparams
    usedby = requests.get(url, headers=headers, auth=(user, pword))
    if usedby.status_code != 200:
        print(f'Could not get list of items related to {oldcsid}. HTTP error response from CSpace server: {usedby.status_code}')
        sys.exit(1)
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
    core = re.search('<ns2:collectionspace_core(.*?)</ns2:collectionspace_core>', record.text, re.DOTALL)
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
    if vocab == 'org':
        vocab2 = 'organization'
    else:
        vocab2 = vocab
    url = baseurl + '/' + vocab + 'authorities/urn:cspace:name(' + vocab2 + ')/items/' + csid
    remove = requests.delete(url, auth=(user, pword))
    return(remove.status_code)


# put all the functions together and execute
def mergeterms():
    oldrefname = getrefname(oldcsid, termvocab)
    newrefname = getrefname(newcsid, termvocab)
    checkrefname(oldrefname, oldcsid, f'old {termvocab} csid')
    checkrefname(newrefname, newcsid, f'new {termvocab} csid')
    getRels(oldcsid)
    countUsedby = getobjs(oldcsid)
    for uri in to_update:
        updateobjs(uri, oldrefname, newrefname)
    if len(failed) == 0:
        if int(countUsedby) == 0:
            print('No uses in object records found, none updated.')
        elif int(countUsedby) < 1000:
            print('All uses in object records were successfully updated.')
        else:
            print(str(len(success)) + ' uses in object records successfully updated.'
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
        print('All relations were successfully deleted.')
    else:
        print('Error deleting the following relations: ' + ', '.join(relFailed))


# data validation for authority type
if sys.argv[1] not in vocabs:
    print(f'\n{sys.argv[1]}: invalid authority use one of the following:\n')
    for v in vocabs:
        print(v)
else:
    termvocab = sys.argv[1]
    if oldcsid == newcsid:
        print('Cannot merge identical terms ' + oldcsid + ' with ' + newcsid)
    else:
        mergeterms()
