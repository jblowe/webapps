SELECT
  cc.id,
  STRING_AGG(DISTINCT gc2.title, '␥') AS highlights_ss,
  STRING_AGG(DISTINCT gc1.title, '␥') AS grouptitle_ss
FROM collectionobjects_common cc

  JOIN hierarchy h1 ON (cc.id = h1.id)
  JOIN relations_common rc ON (h1.name = rc.subjectcsid AND rc.objectdocumenttype = 'Group')
  JOIN hierarchy h2 ON (rc.objectcsid = h2.name)
  LEFT OUTER JOIN groups_common gc1 ON (h2.id = gc1.id)
  LEFT OUTER JOIN groups_common gc2 ON (h2.id = gc2.id AND gc2.title ILIKE '%highlights')
  JOIN misc m ON (gc1.id=m.id AND m.lifecyclestate <> 'deleted')

GROUP BY cc.id