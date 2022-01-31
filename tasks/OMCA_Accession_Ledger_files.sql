SELECT aqc.acquisitionreferencenumber AS acquisitionnumber, va.valueamount AS value, sdg.datedisplaydate,

h1.name AS url,

aqo.accessiondescription AS accessiondescription ,

array_to_string(array_agg(DISTINCT (substring(aqs.item, position(')''' IN aqs.item)+2, length(aqs.item)-position(')''' IN aqs.item)-2))),', ') AS AcquisitionSources,

(SELECT COUNT(rc.objectcsid)
  FROM relations_common rc
  WHERE rc.subjectcsid = h1.name AND objectdocumenttype = 'CollectionObject')AS NumberOfObjects

FROM hierarchy h1
LEFT OUTER JOIN acquisitions_common aqc ON h1.id = aqc.id
LEFT OUTER JOIN acquisitions_omca aqo ON aqc.id = aqo.id
LEFT OUTER JOIN acquisitions_common_acquisitionsources aqs ON aqs.id = aqc.id
LEFT OUTER JOIN hierarchy h2 ON h2.name = (SELECT rc.subjectcsid
                                FROM relations_common rc
                                JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
                                JOIN valuationcontrols_common vc ON (h2.id = vc.id)
                                WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol'
                                ORDER BY vc.valuedate DESC NULLS LAST
                                LIMIT 1)
LEFT OUTER JOIN hierarchy h3 ON h3.parentid = h2.id
LEFT OUTER JOIN valueamounts va ON va.id = h3.id
LEFT OUTER JOIN hierarchy h4 ON h1.id = h4.parentid AND h4.primarytype = 'structuredDateGroup'
LEFT OUTER JOIN structureddategroup sdg ON sdg.id = h4.id
LEFT OUTER JOIN misc ON h1.id = misc.id

WHERE h1.primarytype = 'AcquisitionTenant35' AND RIGHT(sdg.datedisplaydate, 4) = :v OR LEFT(sdg.datedisplaydate, 4) = :v AND misc.lifecyclestate <> 'deleted'

GROUP BY aqc.acquisitionreferencenumber, aqo.sortableacquisitionreferencenumber, h1.name, aqo.accessiondescription, va.valueamount, sdg.datedisplaydate
ORDER BY aqo.sortableacquisitionreferencenumber;
