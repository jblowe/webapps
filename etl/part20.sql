SELECT
  cc.id,
  rg.referencenote AS referencenote_s
FROM collectionobjects_common cc
  LEFT OUTER JOIN hierarchy h1 ON (h1.parentid = cc.id AND h1.name='collectionobjects_common:referenceGroupList' AND h1.pos=0)
  LEFT OUTER JOIN referencegroup rg ON (h1.id = rg.id)
  WHERE rg.referencenote != '';
