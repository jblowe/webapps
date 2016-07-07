SELECT
  coom.computedcurrentlocationdisplay AS computedcurrentlocation,
  -- coc.id AS objectcsid_s,
  regexp_replace(ong.objectname, '^.*\)''(.*)''$', '\1') AS objectname,
  coc.objectnumber AS objectnumber,
  regexp_replace(coc.fieldcollectionplace, '^.*\)''(.*)''$', '\1') AS fieldcollectionplace,
  fcd.datedisplaydate AS fieldcollectiondate,
  coc_collectors.item AS fieldcollector,
  coc.computedcurrentlocation AS computedcurrentlocationrefname,
  coom.sortableobjectnumber AS sortableobjectnumber,
  h1.name AS csid,
  coom.argusdescription AS argusdescription,
  regexp_replace(dethistg.dhname, '^.*\)''(.*)''$', '\1') AS dhname,
  matg.material AS materials,
  regexp_replace(objprdpg.objectproductionperson, '^.*\)''(.*)''$', '\1') AS objectproductionperson,
  regexp_replace(objprdorgg.objectproductionorganization, '^.*\)''(.*)''$', '\1') AS objectproductionorganization,
  regexp_replace(objprdplaceg.objectproductionplace, '^.*\)''(.*)''$', '\1') AS objectproductionplace,
  opd.datedisplaydate AS objectproductiondate,
  (case when coom.donotpublishonweb then 'true' else 'false' end) AS donotpublishonweb,
  regexp_replace(coc.collection, '^.*\)''(.*)''$', '\1') AS collection,
  regexp_replace(coom.ipaudit, '^.*\)''(.*)''$', '\1') AS ipaudit,
  coc_photos.item as photo,
  '' AS copyrightholder,
  '' AS technique

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

  LEFT OUTER JOIN hierarchy h10 ON (h10.parentid = coc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_common:fieldCollectionDateGroup')
  LEFT OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)

  LEFT OUTER JOIN collectionobjects_omca_photos coc_photos ON (coc.id = coc_photos.id AND coc_photos.pos = 0)
  LEFT OUTER JOIN collectionobjects_common_fieldcollectors coc_collectors ON (coc.id = coc_collectors.id AND coc_collectors.pos = 0)
WHERE objectnumber = 'A67.137.93002'
limit 10
;
