SELECT values.name, cc.objectnumber AS obnum, vc.valuationcontrolrefnumber AS vcnum, vc.valuedate AS vcdate,
va.valueamount AS vcamt, co.computedcatalogingsummary AS catsum, co.computedcurrentlocationdisplay AS location, tg.title AS obtitle, gc.title AS grouptitle

FROM (SELECT h1.name,

(SELECT rc.subjectcsid
  FROM relations_common rc
  LEFT JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
  JOIN valuationcontrols_common vc ON (h2.id = vc.id)
  WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol' AND vc.valuedate IS NOT NULL
  ORDER BY vc.valuedate DESC
  LIMIT 1
  ) AS valuationid

FROM hierarchy h1
LEFT OUTER JOIN collectionobjects_omca co ON (co.id = h1.id)
LEFT OUTER JOIN misc ON (h1.id = misc.id)
LEFT OUTER JOIN groups_common gc ON gc.id =  h1.id

WHERE h1.name IN (SELECT rc.subjectcsid FROM relations_common rc
WHERE rc.objectcsid = :v)
AND misc.lifecyclestate <> 'deleted') AS values

INNER JOIN hierarchy h2 ON values.name = h2.name
JOIN collectionobjects_common cc ON cc.id =  h2.id
LEFT JOIN hierarchy h3 ON h3.name = valuationid
LEFT JOIN hierarchy h4 ON h4.parentid = h3.id
LEFT JOIN valueamounts va ON h4.id = va.id
LEFT JOIN valuationcontrols_common vc ON h3.id = vc.id
LEFT JOIN collectionobjects_omca co ON co.id = h2.id
LEFT JOIN hierarchy h6 ON (cc.id = h6.parentid AND h6.name = 'collectionobjects_common:titleGroupList' AND h6.pos = 0)
LEFT OUTER JOIN titlegroup tg ON h6.id = tg.id
LEFT JOIN hierarchy h7 ON h7.name = :v
LEFT OUTER JOIN groups_common gc ON gc.id = h7.id
