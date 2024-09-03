SELECT DISTINCT 
  -- coc.id AS id,
  h1.name AS csid_s,
  coc.objectnumber AS objectnumber_s,
  STRING_AGG(DISTINCT regexp_replace(ong.objectname, '^.*\)''(.*)''$', '\1'),'|') AS objectname_ss,
  regexp_replace(coom.ipaudit, '^.*\)''(.*)''$', '\1') AS ipaudit_s,
  -- coom.ipaudit AS ipaudit_refname_s,
  regexp_replace(coom.copyrightholder, '^.*\)''(.*)''$', '\1') AS copyrightholder_s,
  -- coom.copyrightholder AS copyrightholder_refname_s,
  regexp_replace(objprdpg.objectproductionperson, '^.*\)''(.*)''$', '\1') AS objectproductionperson_s,
  regexp_replace(objprdorgg.objectproductionorganization, '^.*\)''(.*)''$', '\1') AS objectproductionorganization_s,
  STRING_AGG(sdg.datedisplaydate, '|') AS objectproductiondate_ss
  -- STRING_AGG(to_char(sdg.dateearliestscalarvalue + interval '8 hours', 'YYYY-MM-DD'), '␥') AS objectproductionscalardate_ss

FROM collectionobjects_common coc
  JOIN hierarchy h1 ON (h1.id = coc.id)
  JOIN collectionobjects_omca coom ON (coom.id = coc.id)
  JOIN collectionspace_core cx on cx.id = coc.id
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

  LEFT OUTER JOIN hierarchy h2 ON (coc.id = h2.parentid AND h2.primarytype = 'objectNameGroup')
  LEFT OUTER JOIN objectnamegroup ong ON (ong.id = h2.id)

  LEFT OUTER JOIN hierarchy h21 ON (h21.parentid = coc.id AND h21.name='collectionobjects_common:objectProductionOrganizationGroupList' AND h21.pos=0)
  LEFT OUTER JOIN objectproductionorganizationgroup objprdorgg ON (h21.id = objprdorgg.id)
  LEFT OUTER JOIN hierarchy h22 ON (h22.parentid = coc.id AND h22.name='collectionobjects_common:objectProductionPersonGroupList' AND h22.pos=0)
  LEFT OUTER JOIN objectproductionpersongroup objprdpg ON (h22.id = objprdpg.id)

  LEFT OUTER JOIN hierarchy h ON (coc.id = h.parentid AND h.primarytype = 'structuredDateGroup')
  -- AND h.name = 'collectionobjects_common:objectproductionDateGroup')
  LEFT OUTER JOIN structureddategroup sdg ON (sdg.id = h.id)

GROUP BY coc.id, h1.name, coom.id, objprdpg.id, objprdorgg.id
