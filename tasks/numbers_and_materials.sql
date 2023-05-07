SELECT
  coc.objectnumber AS objectnumber_s,
  string_agg(distinct mg.material,', ') AS materials_ss

FROM collectionobjects_common coc
  JOIN hierarchy h1 ON (h1.id = coc.id)
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')
  left join hierarchy as h7 on (coc.id = h7.parentid and h7.primarytype = 'materialGroup')
  left join materialgroup as mg on (h7.id = mg.id)
GROUP BY coc.objectnumber