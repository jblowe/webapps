#!/usr/bin/env /usr/bin/python

import time
import sys
import cgi
import psycopg2


# timeoutcommand = "set statement_timeout to 9000; SET NAMES 'utf8';"
timeoutcommand = "set statement_timeout to 1200000; SET NAMES 'utf8';"

def setupcursor(config, command):
    try:
        dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    except psycopg2.DatabaseError as e:
        sys.stderr.write('DB connection error: %s' % e)
        raise
        # return '%s' % e
    objects = dbconn.cursor()
    objects.execute(timeoutcommand)
    try:
        objects.execute(command)
    except psycopg2.DatabaseError as e:
        sys.stderr.write('DB query error: %s' % e)
        raise
    return objects

def testDB(config):
    dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    objects = dbconn.cursor()
    try:
        objects.execute('set statement_timeout to 5000')
        objects.execute('select * from hierarchy limit 30000')
        return "OK"
    except psycopg2.DatabaseError as e:
        sys.stderr.write('testDB error: %s' % e)
        return '%s' % e
    except:
        sys.stderr.write("some other testDB error!")
        return "Some other failure"


def dbtransaction(command, config):
    dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    cursor = dbconn.cursor()
    cursor.execute(command)


def setquery(type, location, qualifier, institution):

    if type == 'inventory':
        return """
        SELECT distinct on (locationkey,sortableobjectnumber,h3.name)
        (case when ca.computedcrate is Null then l.termdisplayName  
             else concat(l.termdisplayName,
             ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
        replace(concat(l.termdisplayName,
             ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')),' ','0') AS locationkey,
        m.locationdate,
        -- 3
        cc.objectnumber objectnumber,
        cc.numberofobjects objectCount,
        -- 5
        (case when ong.objectName is NULL then '' else regexp_replace(ong.objectName, '^.*\\)''(.*)''$', '\\1') end) objectName,
        rc.subjectcsid movementCsid,
        lc.refname movementRefname,
        -- 8
        rc.objectcsid  objectCsid,
        ''  objectRefname,
        m.id moveid,
        rc.subjectdocumenttype,
        rc.objectdocumenttype,
        cp.sortableobjectnumber sortableobjectnumber,
        -- 14
        ca.computedcrate crateRefname,
        regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1') crate

        FROM loctermgroup l

        join hierarchy h1 on l.id = h1.id
        join locations_common lc on lc.id = h1.parentid
        join movements_common m on m.currentlocation = lc.refname

        join hierarchy h2 on m.id = h2.id
        join relations_common rc on rc.subjectcsid = h2.name

        join hierarchy h3 on rc.objectcsid = h3.name
        join collectionobjects_common cc on (h3.id = cc.id and cc.computedcurrentlocation = lc.refname)

        left outer join collectionobjects_anthropology ca on (ca.id=cc.id)
        left outer join hierarchy h5 on (cc.id = h5.parentid and h5.name = 'collectionobjects_common:objectNameList' and h5.pos=0)
        left outer join objectnamegroup ong on (ong.id=h5.id)

        left outer join collectionobjects_omca cp on (cp.id=cc.id)

        join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')

        WHERE 
           l.termdisplayName = '""" + str(location) + """'

        ORDER BY locationkey,sortableobjectnumber,h3.name desc
        LIMIT 30000"""


    elif type == 'keyinfo' or type == 'packinglist':
        return """
        SELECT distinct on (computedcurrentlocation,objectnumber)
          coom.computedcurrentlocationdisplay AS computedcurrentlocation,
          -- coc.id AS objectcsid_s,
          regexp_replace(ong.objectname, '^.*\\)''(.*)''$', '\\1') AS objectname,
          coc.objectnumber AS objectnumber,
          regexp_replace(coc.fieldcollectionplace, '^.*\\)''(.*)''$', '\\1') AS fieldcollectionplace,
          fcd.datedisplaydate AS fieldcollectiondate,
          regexp_replace(coc_collectors.item, '^.*\\)''(.*)''$', '\\1') AS fieldcollector,
          coc.computedcurrentlocation AS computedcurrentlocationrefname,
          coom.sortableobjectnumber AS sortableobjectnumber,
          h1.name AS csid,
          coom.argusdescription AS argusdescription,
          regexp_replace(dethistg.dhname, '^.*\\)''(.*)''$', '\\1') AS dhname,
          regexp_replace(matg.material, '^.*\\)''(.*)''$', '\\1') AS materials,
          regexp_replace(objprdpg.objectproductionperson, '^.*\\)''(.*)''$', '\\1') AS objectproductionperson,
          regexp_replace(objprdorgg.objectproductionorganization, '^.*\\)''(.*)''$', '\\1') AS objectproductionorganization,
          regexp_replace(objprdplaceg.objectproductionplace, '^.*\\)''(.*)''$', '\\1') AS objectproductionplace,
          opd.datedisplaydate AS objectproductiondate,
          (case when coom.donotpublishonweb then 'true' else 'false' end) AS donotpublishonweb,
          regexp_replace(coc.collection, '^.*\\)''(.*)''$', '\\1') AS collection,
          regexp_replace(coom.ipaudit, '^.*\\)''(.*)''$', '\\1') AS ipaudit,
          coc_photos.item as photo,
          regexp_replace(coom.copyrightholder, '^.*\\)''(.*)''$', '\\1') AS copyrightholder,
          tg.technique AS technique

        FROM loctermgroup l

          join hierarchy hx1 on l.id = hx1.id
          join locations_common lc on lc.id = hx1.parentid
          join movements_common m on m.currentlocation = lc.refname

          join hierarchy hx2 on m.id = hx2.id
          join relations_common rc on rc.subjectcsid = hx2.name

          join hierarchy hx3 on rc.objectcsid = hx3.name
          join collectionobjects_common coc on (hx3.id = coc.id and coc.computedcurrentlocation = lc.refname)

          JOIN hierarchy h1 ON (h1.id = coc.id)
          JOIN collectionobjects_omca coom ON (coom.id = coc.id)
          JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

          LEFT OUTER JOIN hierarchy h2 ON (coc.id=h2.parentid AND h2.name='collectionobjects_common:objectNameList' AND h2.pos=0)
          LEFT OUTER JOIN objectnamegroup ong ON (ong.id=h2.id)
          LEFT OUTER JOIN hierarchy h9 ON (h9.parentid = coc.id AND h9.name='collectionobjects_omca:determinationHistoryGroupList' AND h9.pos=0)
          LEFT OUTER JOIN determinationhistorygroup dethistg ON (h9.id = dethistg.id)
          LEFT OUTER JOIN hierarchy h17 ON (h17.parentid = coc.id AND h17.name='collectionobjects_common:materialGroupList' AND h17.pos=0)
          LEFT OUTER JOIN materialgroup matg ON (h17.id = matg.id)
          LEFT OUTER JOIN hierarchy h21 ON (h21.parentid = coc.id AND h21.name='collectionobjects_common:objectProductionOrganizationGroupList' AND h21.pos=0)
          LEFT OUTER JOIN objectproductionorganizationgroup objprdorgg ON (h21.id = objprdorgg.id)
          LEFT OUTER JOIN hierarchy h22 ON (h22.parentid = coc.id AND h22.name='collectionobjects_common:objectProductionPersonGroupList' AND h22.pos=0)
          LEFT OUTER JOIN objectproductionpersongroup objprdpg ON (h22.id = objprdpg.id)
          LEFT OUTER JOIN hierarchy h23 ON (h23.parentid = coc.id AND h23.name='collectionobjects_common:objectProductionPlaceGroupList' AND h23.pos=0)
          LEFT OUTER JOIN objectproductionplacegroup objprdplaceg ON (h23.id = objprdplaceg.id)
          LEFT OUTER JOIN hierarchy h24 ON (h24.parentid = coc.id AND h24.name='collectionobjects_common:objectProductionDateGroupList' AND h24.pos=0)
          LEFT OUTER JOIN structureddategroup opd ON (h24.id = opd.id)
          LEFT OUTER JOIN hierarchy h10 ON (h10.parentid = coc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_common:fieldCollectionDateGroup')
          LEFT OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)
          LEFT OUTER JOIN hierarchy h25 ON (h25.parentid=coc.id AND h25.primarytype='techniqueGroup' AND h25.pos = 0 )
          LEFT OUTER JOIN techniquegroup tg ON (tg.id=h25.id)

          LEFT OUTER JOIN collectionobjects_omca_photos coc_photos ON (coc.id = coc_photos.id AND coc_photos.pos = 0)
          LEFT OUTER JOIN collectionobjects_common_fieldcollectors coc_collectors ON (coc.id = coc_collectors.id AND coc_collectors.pos = 0)

        WHERE
           l.termdisplayName = '""" + str(location) + """'

        ORDER BY computedcurrentlocation,objectnumber asc
        LIMIT 500
        """


def getlocations(location1, location2, num2ret, config, updateType, institution):

    debug = False

    result = []

    for loc in getloclist('set', location1, '', num2ret, config):
        getobjects = setquery(updateType, loc[0], '', institution)

        try:
            elapsedtime = time.time()
            objects = setupcursor(config, getobjects)
            elapsedtime = time.time() - elapsedtime
            if debug: sys.stderr.write('all objects: %s :: %s\n' % (loc[0], elapsedtime))
        except psycopg2.DatabaseError as e:
            sys.stderr.write('getlocations select error: %s' % e)
            #return result
            raise
        except:
            sys.stderr.write("some other getlocations database error!")
            #return result
            raise

        try:
            rows = [list(item) for item in objects.fetchall()]
        except psycopg2.DatabaseError as e:
            sys.stderr.write("fetchall getlocations database error!")

        if debug: sys.stderr.write('number objects to be checked: %s\n' % len(rows))
        try:
            for row in rows:
                result.append(row)
        except:
            sys.stderr.write("other getobjects error: %s" % len(rows))
            raise

    return result


def getgrouplist(group, num2ret, config):
    if int(num2ret) > 30000: num2ret = 30000
    if int(num2ret) < 1:    num2ret = 1
    institution = config.get('info', 'institution')

    getobjects = """SELECT DISTINCT ON (sortableobjectnumber)
          coom.computedcurrentlocationdisplay AS computedcurrentlocation,
          -- coc.id AS objectcsid_s,
          regexp_replace(ong.objectname, '^.*\\)''(.*)''$', '\\1') AS objectname,
          coc.objectnumber AS objectnumber,
          regexp_replace(coc.fieldcollectionplace, '^.*\\)''(.*)''$', '\\1') AS fieldcollectionplace,
          fcd.datedisplaydate AS fieldcollectiondate,
          regexp_replace(coc_collectors.item, '^.*\\)''(.*)''$', '\\1') AS fieldcollector,
          coc.computedcurrentlocation AS computedcurrentlocationrefname,
          coom.sortableobjectnumber AS sortableobjectnumber,
          hrc.name AS csid,
          coom.argusdescription AS argusdescription,
          regexp_replace(dethistg.dhname, '^.*\\)''(.*)''$', '\\1') AS dhname,
          regexp_replace(matg.material, '^.*\\)''(.*)''$', '\\1') AS materials,
          regexp_replace(objprdpg.objectproductionperson, '^.*\\)''(.*)''$', '\\1') AS objectproductionperson,
          regexp_replace(objprdorgg.objectproductionorganization, '^.*\\)''(.*)''$', '\\1') AS objectproductionorganization,
          regexp_replace(objprdplaceg.objectproductionplace, '^.*\\)''(.*)''$', '\\1') AS objectproductionplace,
          opd.datedisplaydate AS objectproductiondate,
          (case when coom.donotpublishonweb then 'true' else 'false' end) AS donotpublishonweb,
          regexp_replace(coc.collection, '^.*\\)''(.*)''$', '\\1') AS collection,
          regexp_replace(coom.ipaudit, '^.*\\)''(.*)''$', '\\1') AS ipaudit,
          coc_photos.item as photo,
          regexp_replace(coom.copyrightholder, '^.*\\)''(.*)''$', '\\1') AS copyrightholder,
          tg.technique AS technique

FROM groups_common gc

          join hierarchy hgc ON (gc.id = hgc.id)
          join misc mc1 on (gc.id = mc1.id AND mc1.lifecyclestate <> 'deleted')
          join relations_common rc ON (hgc.name = rc.subjectcsid)
          join hierarchy hrc ON (rc.objectcsid = hrc.name)
          left outer join collectionobjects_common coc ON (hrc.id = coc.id)

          JOIN collectionobjects_omca coom ON (coom.id = coc.id)
          JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

          LEFT OUTER JOIN hierarchy h2 ON (coc.id=h2.parentid AND h2.name='collectionobjects_common:objectNameList' AND h2.pos=0)
          LEFT OUTER JOIN objectnamegroup ong ON (ong.id=h2.id)
          LEFT OUTER JOIN hierarchy h9 ON (h9.parentid = coc.id AND h9.name='collectionobjects_omca:determinationHistoryGroupList' AND h9.pos=0)
          LEFT OUTER JOIN determinationhistorygroup dethistg ON (h9.id = dethistg.id)
          LEFT OUTER JOIN hierarchy h17 ON (h17.parentid = coc.id AND h17.name='collectionobjects_common:materialGroupList' AND h17.pos=0)
          LEFT OUTER JOIN materialgroup matg ON (h17.id = matg.id)
          LEFT OUTER JOIN hierarchy h21 ON (h21.parentid = coc.id AND h21.name='collectionobjects_common:objectProductionOrganizationGroupList' AND h21.pos=0)
          LEFT OUTER JOIN objectproductionorganizationgroup objprdorgg ON (h21.id = objprdorgg.id)
          LEFT OUTER JOIN hierarchy h22 ON (h22.parentid = coc.id AND h22.name='collectionobjects_common:objectProductionPersonGroupList' AND h22.pos=0)
          LEFT OUTER JOIN objectproductionpersongroup objprdpg ON (h22.id = objprdpg.id)
          LEFT OUTER JOIN hierarchy h23 ON (h23.parentid = coc.id AND h23.name='collectionobjects_common:objectProductionPlaceGroupList' AND h23.pos=0)
          LEFT OUTER JOIN objectproductionplacegroup objprdplaceg ON (h23.id = objprdplaceg.id)
          LEFT OUTER JOIN hierarchy h24 ON (h24.parentid = coc.id AND h24.name='collectionobjects_common:objectProductionDateGroupList' AND h24.pos=0)
          LEFT OUTER JOIN structureddategroup opd ON (h24.id = opd.id)
          LEFT OUTER JOIN hierarchy h10 ON (h10.parentid = coc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_common:fieldCollectionDateGroup')
          LEFT OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)
          LEFT OUTER JOIN hierarchy h25 ON (h25.parentid=coc.id AND h25.primarytype='techniqueGroup' AND h25.pos = 0 )
          LEFT OUTER JOIN techniquegroup tg ON (tg.id=h25.id)

          LEFT OUTER JOIN collectionobjects_omca_photos coc_photos ON (coc.id = coc_photos.id AND coc_photos.pos = 0)
          LEFT OUTER JOIN collectionobjects_common_fieldcollectors coc_collectors ON (coc.id = coc_collectors.id AND coc_collectors.pos = 0)


WHERE
   gc.title='""" + group + """'
ORDER BY sortableobjectnumber asc
limit """ + str(num2ret)


    try:
        objects = setupcursor(config, getobjects)
        #for object in objects.fetchall():
        #print(object)
        return [list(item) for item in objects.fetchall()], ''
    except:
        return [], 'problem with group query'


def getloclist(searchType, location1, location2, num2ret, config):
    # 'set' means 'next num2ret locations', otherwise prefix match
    if searchType == 'set':
        whereclause = "WHERE locationkey >= replace('" + location1 + "',' ','0')"
    elif searchType == 'exact':
        whereclause = "WHERE locationkey = replace('" + location1 + "',' ','0')"
    elif searchType == 'prefix':
        whereclause = "WHERE locationkey LIKE replace('" + location1 + "%',' ','0')"
    elif searchType == 'range':
        whereclause = "WHERE locationkey >= replace('" + location1 + "',' ','0') AND locationkey <= replace('" + location2 + "',' ','0')"

    if int(num2ret) > 30000: num2ret = 30000
    if int(num2ret) < 1:    num2ret = 1

    getobjects = """
select * from (
select termdisplayname,replace(termdisplayname,' ','0') locationkey 
FROM loctermgroup ltg
INNER JOIN hierarchy h_ltg
        ON h_ltg.id=ltg.id
INNER JOIN hierarchy h_loc
        ON h_loc.id=h_ltg.parentid
INNER JOIN misc
        ON misc.id=h_loc.id and misc.lifecyclestate <> 'deleted'
) as t
""" + whereclause + """
order by locationkey
limit """ + str(num2ret)

    try:
        objects = setupcursor(config, getobjects)
        #for object in objects.fetchall():
        #print(object)
        # return objects.fetchall()
        return [list(item) for item in objects.fetchall()]
    except:
        raise


def getobjlist(searchType, object1, object2, num2ret, config):
    query1 = """
    SELECT objectNumber,
cp.sortableobjectnumber
FROM collectionobjects_common cc
left outer join collectionobjects_omca cp on (cp.id=cc.id)
INNER JOIN hierarchy h1
        ON cc.id=h1.id
INNER JOIN misc
        ON misc.id=h1.id and misc.lifecyclestate <> 'deleted'
WHERE
     cc.objectNumber = '%s'"""

    if int(num2ret) > 1000: num2ret = 1000
    if int(num2ret) < 1:    num2ret = 1

    try:
        objects = setupcursor(config, query1 % object1)
        (object1, sortkey1) = objects.fetchone()
        objects = setupcursor(config, query1 % object2)
        (object2, sortkey2) = objects.fetchone()
    except:
        return [], 'problem'

    # 'set' means 'next num2ret objects', otherwise prefix match
    if searchType == 'set':
        whereclause = "WHERE sortableobjectnumber >= '" + sortkey1 + "'"
    elif searchType == 'prefix':
        whereclause = "WHERE sortableobjectnumber LIKE '" + sortkey1 + "%'"
    elif searchType == 'range':
        whereclause = "WHERE sortableobjectnumber >= '" + sortkey1 + "' AND sortableobjectnumber <= '" + sortkey2 + "'"

        getobjects = """
SELECT
  coom.computedcurrentlocationdisplay AS computedcurrentlocation,
  -- coc.id AS objectcsid_s,
  regexp_replace(ong.objectname, '^.*\\)''(.*)''$', '\\1') AS objectname,
  coc.objectnumber AS objectnumber,
  regexp_replace(coc.fieldcollectionplace, '^.*\\)''(.*)''$', '\\1') AS fieldcollectionplace,
  fcd.datedisplaydate AS fieldcollectiondate,
  regexp_replace(coc_collectors.item, '^.*\\)''(.*)''$', '\\1') AS fieldcollector,
  coc.computedcurrentlocation AS computedcurrentlocationrefname,
  coom.sortableobjectnumber AS sortableobjectnumber,
  h1.name AS csid,
  coom.argusdescription AS argusdescription,
  regexp_replace(dethistg.dhname, '^.*\\)''(.*)''$', '\\1') AS dhname,
  regexp_replace(matg.material, '^.*\\)''(.*)''$', '\\1') AS materials,
  regexp_replace(objprdpg.objectproductionperson, '^.*\\)''(.*)''$', '\\1') AS objectproductionperson,
  regexp_replace(objprdorgg.objectproductionorganization, '^.*\\)''(.*)''$', '\\1') AS objectproductionorganization,
  regexp_replace(objprdplaceg.objectproductionplace, '^.*\\)''(.*)''$', '\\1') AS objectproductionplace,
  opd.datedisplaydate AS objectproductiondate,
  (case when coom.donotpublishonweb then 'true' else 'false' end) AS donotpublishonweb,
  regexp_replace(coc.collection, '^.*\\)''(.*)''$', '\\1') AS collection,
  regexp_replace(coom.ipaudit, '^.*\\)''(.*)''$', '\\1') AS ipaudit,
  coc_photos.item as photo,
  regexp_replace(coom.copyrightholder, '^.*\\)''(.*)''$', '\\1') AS copyrightholder,
  tg.technique AS technique

FROM collectionobjects_omca coom
  left outer join collectionobjects_common coc on (coom.id=coc.id)
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')
  JOIN hierarchy h1 ON (h1.id = coc.id)

  LEFT OUTER JOIN hierarchy h2 ON (coc.id=h2.parentid AND h2.name='collectionobjects_common:objectNameList' AND h2.pos=0)
  LEFT OUTER JOIN objectnamegroup ong ON (ong.id=h2.id)
  LEFT OUTER JOIN hierarchy h9 ON (h9.parentid = coc.id AND h9.name='collectionobjects_omca:determinationHistoryGroupList' AND h9.pos=0)
  LEFT OUTER JOIN determinationhistorygroup dethistg ON (h9.id = dethistg.id)
  LEFT OUTER JOIN hierarchy h17 ON (h17.parentid = coc.id AND h17.name='collectionobjects_common:materialGroupList' AND h17.pos=0)
  LEFT OUTER JOIN materialgroup matg ON (h17.id = matg.id)
  LEFT OUTER JOIN hierarchy h21 ON (h21.parentid = coc.id AND h21.name='collectionobjects_common:objectProductionOrganizationGroupList' AND h21.pos=0)
  LEFT OUTER JOIN objectproductionorganizationgroup objprdorgg ON (h21.id = objprdorgg.id)
  LEFT OUTER JOIN hierarchy h22 ON (h22.parentid = coc.id AND h22.name='collectionobjects_common:objectProductionPersonGroupList' AND h22.pos=0)
  LEFT OUTER JOIN objectproductionpersongroup objprdpg ON (h22.id = objprdpg.id)
  LEFT OUTER JOIN hierarchy h23 ON (h23.parentid = coc.id AND h23.name='collectionobjects_common:objectProductionPlaceGroupList' AND h23.pos=0)
  LEFT OUTER JOIN objectproductionplacegroup objprdplaceg ON (h23.id = objprdplaceg.id)
  LEFT OUTER JOIN hierarchy h24 ON (h24.parentid = coc.id AND h24.name='collectionobjects_common:objectProductionDateGroupList' AND h24.pos=0)
  LEFT OUTER JOIN structureddategroup opd ON (h24.id = opd.id)
  LEFT OUTER JOIN hierarchy h10 ON (h10.parentid = coc.id AND h10.name = 'collectionobjects_common:fieldCollectionDateGroup')
  LEFT OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)
  LEFT OUTER JOIN hierarchy h25 ON (h25.parentid=coc.id AND h25.primarytype='techniqueGroup' AND h25.pos = 0 )
  LEFT OUTER JOIN techniquegroup tg ON (tg.id=h25.id)

  LEFT OUTER JOIN collectionobjects_omca_photos coc_photos ON (coc.id = coc_photos.id AND coc_photos.pos = 0)
  LEFT OUTER JOIN collectionobjects_common_fieldcollectors coc_collectors ON (coc.id = coc_collectors.id AND coc_collectors.pos = 0)
""" + whereclause + """
ORDER BY sortableobjectnumber
limit """ + str(num2ret)

    objects = setupcursor(config, getobjects)
    #for object in objects.fetchall():
    #print(object)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()], None


def findcurrentlocation(csid, config):

    getloc = "select findcurrentlocation('" + csid + "')"

    try:
        objects = setupcursor(config, getloc)
    except:
        return "findcurrentlocation error"

    return objects.fetchone()[0]


def getrefname(table, term, config):

    if term == None or term == '':
        return ''

    if table in ('collectionobjects_common_fieldcollectors', 'collectionobjects_common_briefdescriptions',
                 'acquisitions_common_owners'):
        column = 'item'
    else:
        column = 'refname'

    if table == 'collectionobjects_common_briefdescriptions':
        query = "SELECT item FROM collectionobjects_common_briefdescriptions WHERE item ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    elif table == 'omcaaltnumgroup':
        query = "SELECT omcaaltnum FROM omcaaltnumgroup WHERE omcaaltnum ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    elif table == 'omcaaltnumgroup_type':
        query = "SELECT omcaaltnumtype FROM omcaaltnumgroup WHERE omcaaltnum ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    else:
        query = "select %s from %s x join misc ON misc.id = x.id AND misc.lifecyclestate <> 'deleted' where %s ILIKE '%%''%s''%%' LIMIT 1" % (
            column, table, column, term.replace("'", "''"))

    try:
        objects = setupcursor(config, query)
        return objects.fetchone()[0]
    except:
        return ''
        raise


def findrefnames(table, termlist, config):

    result = []
    for t in termlist:
        query = "select refname from %s where refname ILIKE '%%''%s''%%'" % (table, t.replace("'", "''"))

        try:
            objects = setupcursor(config, query)
            refname = objects.fetchone()
            result.append([t, refname])
        except:
            raise
            return "findrefnames error"

    return result


def findvocabnames(vocab, term, config):

    result = []
    query = "select refname from vocabularyitems_common vc where refname ilike '%%%s%%' and displayname  = '%s'" % (vocab, term.replace("'", "''"))

    try:
        objects = setupcursor(config, query)
        refname = objects.fetchone()
        if refname is None:
            return refname
        else:
            return refname[0]
    except:
        raise
        return "findrefnames error"


def finddoctypes(table, doctype, config):

    query = "select %s,count(*) as n from %s group by %s;" % (doctype,table,doctype)

    try:
        doctypes = setupcursor(config,query)
        # return doctypes.fetchall()
        return [list(item) for item in doctypes.fetchall()]
    except:
        raise
        return "finddoctypes error"


def getobjinfo(museumNumber, config):

    getobjects = """
    SELECT co.objectnumber,
    n.objectname,
    co.numberofobjects,
    regexp_replace(fcp.item, '^.*\\)''(.*)''$', '\\1') AS fieldcollectionplace,
    regexp_replace(apg.assocpeople, '^.*\\)''(.*)''$', '\\1') AS culturalgroup,
    regexp_replace(pef.item, '^.*\\)''(.*)''$', '\\1') AS  ethnographicfilecode
FROM collectionobjects_common co
LEFT OUTER JOIN hierarchy h1 ON (co.id = h1.parentid AND h1.primarytype='objectNameGroup' AND h1.pos=0)
LEFT OUTER JOIN objectnamegroup n ON (n.id=h1.id)
LEFT OUTER JOIN collectionobjects_omca_omcafieldcollectionplacelist fcp ON (co.id=fcp.id AND fcp.pos=0)
LEFT OUTER JOIN collectionobjects_omca_omcaethnographicfilecodelist pef on (pef.id=co.id and pef.pos=0)
LEFT OUTER JOIN collectionobjects_common_responsibledepartments cm ON (co.id=cm.id AND cm.pos=0)
LEFT OUTER JOIN hierarchy h2 ON (co.id=h2.parentid AND h2.primarytype='assocPeopleGroup' AND h2.pos=0)
LEFT OUTER JOIN assocpeoplegroup apg ON apg.id=h2.id
JOIN misc ON misc.id = co.id AND misc.lifecyclestate <> 'deleted'
WHERE co.objectnumber = '%s' LIMIT 1""" % museumNumber

    objects = setupcursor(config, getobjects)
    #for ob in objects.fetchone():
    #print(ob)
    return objects.fetchone()


def gethierarchy(query, config):
    institution = config.get('info', 'institution')

    if query == 'taxonomy':
        gethierarchy = """
SELECT DISTINCT
        regexp_replace(child.refname, '^.*\\)''(.*)''$', '\\1') AS Child, 
        regexp_replace(parent.refname, '^.*\\)''(.*)''$', '\\1') AS Parent, 
        h1.name AS ChildKey,
        h2.name AS ParentKey
FROM taxon_common child
JOIN misc ON (misc.id = child.id)
FULL OUTER JOIN hierarchy h1 ON (child.id = h1.id)
FULL OUTER JOIN relations_common rc ON (h1.name = rc.subjectcsid)
FULL OUTER JOIN hierarchy h2 ON (rc.objectcsid = h2.name)
FULL OUTER JOIN taxon_common parent ON (parent.id = h2.id)
WHERE child.refname LIKE 'urn:cspace:%s.cspace.berkeley.edu:taxonomyauthority:name(taxon):item:name%%'
AND misc.lifecyclestate <> 'deleted'
ORDER BY Parent, Child
""" % institution
    elif query != 'places':
        gethierarchy = """
SELECT DISTINCT
        regexp_replace(child.refname, '^.*\\)''(.*)''$', '\\1') AS Child, 
        regexp_replace(parent.refname, '^.*\\)''(.*)''$', '\\1') AS Parent, 
        h1.name AS ChildKey,
        h2.name AS ParentKey
FROM concepts_common child
JOIN misc ON (misc.id = child.id)
FULL OUTER JOIN hierarchy h1 ON (child.id = h1.id)
FULL OUTER JOIN relations_common rc ON (h1.name = rc.subjectcsid)
FULL OUTER JOIN hierarchy h2 ON (rc.objectcsid = h2.name)
FULL OUTER JOIN concepts_common parent ON (parent.id = h2.id)
WHERE child.refname LIKE 'urn:cspace:%s.cspace.berkeley.edu:conceptauthorities:name({0})%%'
AND misc.lifecyclestate <> 'deleted'
ORDER BY Parent, Child""" % institution
        gethierarchy = gethierarchy.format(query)
    else:
        if institution == 'omca': tenant = 'Tenant15'
        if institution == 'botgarden': tenant = 'Tenant35'
        gethierarchy = """
SELECT DISTINCT
	regexp_replace(tc.refname, '^.*\\)''(.*)''$', '\\1') Place,
	regexp_replace(tc2.refname, '^.*\\)''(.*)''$', '\\1') ParentPlace,
	h.name ChildKey,
	h2.name ParentKey
FROM public.places_common tc
	INNER JOIN misc m ON (tc.id=m.id AND m.lifecyclestate<>'deleted')
	INNER JOIN hierarchy h ON (tc.id = h.id AND h.primarytype='Placeitem%s')
	LEFT OUTER JOIN public.relations_common rc ON (h.name = rc.subjectcsid)
	LEFT OUTER JOIN hierarchy h2 ON (h2.primarytype = 'Placeitem%s' AND rc.objectcsid = h2.name)
	LEFT OUTER JOIN places_common tc2 ON (tc2.id = h2.id)
ORDER BY ParentPlace, Place""" % (tenant, tenant)

    objects = setupcursor(config, gethierarchy)
    #return objects.fetchall()
    return [list(item) for item in objects.fetchall()]


def getCSID(argType, arg, config):

    if argType == 'objectnumber':
        query = """SELECT h.name from collectionobjects_common cc
JOIN hierarchy h on h.id=cc.id
WHERE objectnumber = '%s'""" % arg.replace("'", "''")
    elif argType == 'crateName':
        query = """SELECT h.name FROM collectionobjects_anthropology ca
JOIN hierarchy h on h.id=ca.id
WHERE computedcrate ILIKE '%%''%s''%%'""" % arg.replace("'", "''")
    elif argType == 'placeName':
        query = """SELECT h.name from places_common pc
JOIN hierarchy h on h.id=pc.id
WHERE pc.refname ILIKE '%""" + arg.replace("'", "''") + "%%'"

    objects = setupcursor(config, query)
    return objects.fetchone()


def getCSIDs(argType, arg, config):

    if argType == 'crateName':
        query = """SELECT h.name FROM collectionobjects_anthropology ca
JOIN hierarchy h on h.id=ca.id
WHERE computedcrate ILIKE '%%''%s''%%'""" % arg.replace("'", "''")

    objects = setupcursor(config, query)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()]


def findparents(refname, config):

    query = """WITH RECURSIVE ethnculture_hierarchyquery as (
SELECT regexp_replace(cc.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCulture,
      cc.refname,
      rc.objectcsid broaderculturecsid,
      regexp_replace(cc2.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCultureBroader,
      0 AS level
FROM concepts_common cc
JOIN hierarchy h ON (cc.id = h.id)
LEFT OUTER JOIN relations_common rc ON (h.name = rc.subjectcsid)
LEFT OUTER JOIN hierarchy h2 ON (rc.relationshiptype='hasBroader' AND rc.objectcsid = h2.name)
LEFT OUTER JOIN concepts_common cc2 ON (cc2.id = h2.id)
WHERE cc.refname LIKE 'urn:cspace:omca.cspace.berkeley.edu:conceptauthorities:name(concept)%%'
and cc.refname = '%s'
UNION ALL
SELECT regexp_replace(cc.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCulture,
      cc.refname,
      rc.objectcsid broaderculturecsid,
      regexp_replace(cc2.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCultureBroader,
      ech.level-1 AS level
FROM concepts_common cc
JOIN hierarchy h ON (cc.id = h.id)
LEFT OUTER JOIN relations_common rc ON (h.name = rc.subjectcsid)
LEFT OUTER JOIN hierarchy h2 ON (rc.relationshiptype='hasBroader' AND rc.objectcsid = h2.name)
LEFT OUTER JOIN concepts_common cc2 ON (cc2.id = h2.id)
INNER JOIN ethnculture_hierarchyquery AS ech ON h.name = ech.broaderculturecsid)
SELECT ethnCulture, refname, level
FROM ethnculture_hierarchyquery
order by level""" % refname.replace("'", "''")

    try:
        objects = setupcursor(config, query)
        # return objects.fetchall()
        return [list(item) for item in objects.fetchall()]
    except:
        #raise
        return [["findparents error"]]

def getCSIDDetail(config, csid, detail):
    
    if detail == 'fieldcollectionplace':
        query = """SELECT substring(pfc.item, position(')''' IN pfc.item)+2, LENGTH(pfc.item)-position(')''' IN pfc.item)-2)
AS fieldcollectionplace

FROM collectionobjects_omca_omcafieldcollectionplacelist pfc
LEFT OUTER JOIN HIERARCHY h1 on (pfc.id=h1.id and pfc.pos = 0)

WHERE h1.name = '%s'""" % csid
    elif detail == 'assocpeoplegroup':
        query = """SELECT substring(apg.assocpeople, position(')''' IN apg.assocpeople)+2, LENGTH(apg.assocpeople)-position(')''' IN apg.assocpeople)-2)
as culturalgroup

FROM collectionobjects_common cc

left outer join hierarchy h1 on (cc.id=h1.id)
left outer join hierarchy h2 on (cc.id=h2.parentid and h2.primarytype =
'assocPeopleGroup' and (h2.pos=0 or h2.pos is null))
left outer join assocpeoplegroup apg on (apg.id=h2.id)

WHERE h1.name = '%s'""" % csid
    elif detail == 'objcount':
        query = """SELECT cc.numberofobjects
FROM collectionobjects_common cc
left outer join hierarchy h1 on (cc.id=h1.id)
WHERE h1.name = '%s'""" % csid
    elif detail == 'objNumber':
        query = """SELECT cc.objectnumber
FROM collectionobjects_common cc
left outer join hierarchy h1 on (cc.id=h1.id)
WHERE h1.name = '%s'""" % csid
    elif detail == 'material':
        pass
    elif detail == 'taxon':
        pass
    else:
        return ''
    try:
        objects = setupcursor(config, query)
        return objects.fetchone()[0]
    except:
        return ''


def getDisplayName(config, refname):


    query = """SELECT REGEXP_REPLACE(pog.anthropologyplaceowner, '^.*\)''(.*)''$', '\\1')
FROM anthropologyplaceownergroup pog
WHERE pog.anthropologyplaceowner LIKE '""" + refname + "%'"

    objects = setupcursor(config,query)
    return objects.fetchone()
