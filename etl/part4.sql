SELECT
  cc.id,
  ac.acquisitionreferencenumber                     AS acquisitionreferencenumber_s,
  sad1.datedisplaydate                              AS accessiondate_s,
  sad1.dateearliestscalarvalue::DATE                AS accessiondate_dt,
  sad2.datedisplaydate                              AS acquisitiondate_s,
  ac.creditline                                     AS creditline_s
FROM collectionobjects_common cc
  JOIN hierarchy h1 ON (h1.id = cc.id)
  JOIN relations_common rca ON (h1.name = rca.subjectcsid AND rca.objectdocumenttype = 'Acquisition')
  JOIN hierarchy hac ON (hac.name = rca.objectcsid AND (hac.pos = 0 OR hac.pos IS NULL))
  JOIN acquisitions_common ac ON (hac.id = ac.id)
  LEFT OUTER JOIN hierarchy had1 ON (ac.id = had1.parentid AND had1.primarytype = 'structuredDateGroup' AND
                                     had1.name = 'acquisitions_common:accessionDateGroup' AND
                                     (had1.pos = 0 OR had1.pos IS NULL))
  LEFT OUTER JOIN structureddategroup sad1 ON (sad1.id = had1.id)
  LEFT OUTER JOIN hierarchy had2 ON (ac.id = had2.parentid AND had2.primarytype = 'structuredDateGroup' AND
                                     had2.name = 'acquisitions_common:acquisitionDateGroupList' AND
                                     (had2.pos = 0 OR had2.pos IS NULL))
  LEFT OUTER JOIN structureddategroup sad2 ON (sad2.id = had2.id)
