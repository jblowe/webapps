SELECT
  coc.objectnumber AS objectnumber_s,
  matg.materialsource AS materials_s

FROM collectionobjects_common coc
  JOIN hierarchy h1 ON (h1.id = coc.id)
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

  LEFT OUTER JOIN hierarchy h17 ON (h17.parentid = coc.id AND h17.name='collectionobjects_common:materialGroupList' AND h17.pos=0)
  LEFT OUTER JOIN materialgroup matg ON (h17.id = matg.id)
