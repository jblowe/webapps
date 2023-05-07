SELECT
  coc.objectnumber AS objectnumber_s,
  regexp_replace(ong.objectname, '^.*\)''(.*)''$', '\1') AS objectname_s

FROM collectionobjects_common coc
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')
  LEFT OUTER JOIN hierarchy h2 ON (coc.id=h2.parentid AND h2.name='collectionobjects_common:objectNameList' AND h2.pos=0)
  LEFT OUTER JOIN objectnamegroup ong ON (ong.id=h2.id)
