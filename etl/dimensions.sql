SELECT
  h1.name AS csid_s,
  coc.id AS objectcsid_s,

  mpg.dimensionsummary AS dimensionsummary_s,
  regexp_replace(mpg.measuredpart, '^.*\)''(.*)''$', '\1') AS measuredpart_s

FROM collectionobjects_common coc
  JOIN hierarchy h1 ON (h1.id = coc.id)
  JOIN collectionobjects_omca coom ON (coom.id = coc.id)
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

  LEFT OUTER JOIN hierarchy h18 ON (h18.parentid = coc.id AND h18.name='collectionobjects_common:measuredPartGroupList' AND h18.pos=0)
  LEFT OUTER JOIN measuredpartgroup mpg ON (h18.id = mpg.id)
