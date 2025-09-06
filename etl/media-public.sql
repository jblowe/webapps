SELECT
h2.name objectcsid,
cc.objectnumber,
h1.name mediacsid,
mc.description,
b.name,
mc.creator creatorRefname,
mc.creator creator,
mc.blobcsid,
mc.copyrightstatement,
mc.identificationnumber,
mc.rightsholder rightsholderRefname,
mc.rightsholder rightsholder,
mc.contributor,
mo.approveforpublic,
-- need this CASE statement because there are null values
CASE WHEN mo.isprimary is true THEN true ELSE false END AS isprimary_computed,
c.data AS md5,
c.length

FROM media_common mc

JOIN misc ON (mc.id = misc.id AND misc.lifecyclestate <> 'deleted')
JOIN media_omca mo on (mc.id = mo.id)
LEFT OUTER JOIN hierarchy h1 ON (h1.id = mc.id)
INNER JOIN relations_common r on (h1.name = r.objectcsid)
LEFT OUTER JOIN hierarchy h2 on (r.subjectcsid = h2.name)
LEFT OUTER JOIN collectionobjects_common cc on (h2.id = cc.id)

JOIN hierarchy h3 ON (mc.blobcsid = h3.name)
LEFT OUTER JOIN blobs_common b on (h3.id = b.id)
LEFT OUTER JOIN hierarchy h4 ON (b.repositoryid = h4.parentid AND h4.primarytype = 'content')
LEFT OUTER JOIN content c ON (h4.id = c.id)

WHERE mo.approveforpublic

ORDER BY cc.objectnumber ASC,isprimary_computed DESC,mc.identificationnumber DESC
