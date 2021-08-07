\echo Total number of collection objects not deaccessioned or deleted that have a record Status of 'Approved and updated'
SELECT count (cc.id)
FROM collectionobjects_common cc
INNER JOIN hierarchy h1 ON h1.id = cc.id
INNER JOIN misc ON cc.id = misc.id
WHERE cc.recordstatus = 'urn:cspace:museumca.org:vocabularies:name(recordStatus):item:name(Approvedandupdated1557761400030)''Approved and updated'''
AND h1.name NOT IN (
   SELECT subjectcsid FROM relations_common
   WHERE subjectdocumenttype = 'CollectionObject'
   AND objectdocumenttype = 'ObjectExit'
)
AND misc.lifecyclestate <> 'deleted';

\echo Total number of cataloging procedures that are not deleted (does include deacessions though)
SELECT count(cc.id)
FROM collectionobjects_common cc
INNER JOIN misc ON cc.id = misc.id
WHERE misc.lifecyclestate <> 'deleted';

\echo Total number of media handling procedures that are not deleted
SELECT count(mc.id)
FROM media_common mc
INNER JOIN misc ON mc.id = misc.id
WHERE misc.lifecyclestate <> 'deleted';

\echo Total number of conservation procedures that are not deleted
SELECT count(cc.id)
FROM conservation_common cc
INNER JOIN misc ON cc.id = misc.id
WHERE misc.lifecyclestate <> 'deleted';
