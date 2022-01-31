SELECT values.name, cc.objectnumber AS obnum, vc.valuationcontrolrefnumber AS vcnum, vc.valuedate AS vcdate, va.valueamount AS vcamt, co.computedcurrentlocationdisplay AS location,
substring(ong.objectName, position(')''' IN ong.objectName)+2, length(ong.objectName)-position(')''' IN ong.objectName)-2) AS objectName,
tg.title AS obtitle,
substring(oppg.objectProductionPerson, position(')''' IN oppg.objectProductionPerson)+2, length(oppg.objectProductionPerson)-position(')''' IN oppg.objectProductionPerson)-2) AS maker

FROM (SELECT h1.name,

(SELECT rc.subjectcsid
  FROM relations_common rc
  JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
  JOIN valuationcontrols_common vc ON (h2.id = vc.id)
  WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol' AND vc.valuedate IS NOT NULL
  ORDER BY vc.valuedate DESC
  LIMIT 1
  ) AS valuationid

FROM hierarchy h1
LEFT OUTER JOIN collectionobjects_omca co ON (co.id = h1.id)
LEFT OUTER JOIN misc ON (h1.id = misc.id)


WHERE misc.lifecyclestate <> 'deleted') AS values

JOIN hierarchy h2 ON values.name = h2.name
JOIN collectionobjects_common cc ON cc.id =  h2.id
JOIN hierarchy h3 ON h3.name = valuationid
JOIN hierarchy h4 ON h4.parentid = h3.id
JOIN valueamounts va ON h4.id = va.id
JOIN valuationcontrols_common vc ON h3.id = vc.id
JOIN collectionobjects_omca co ON co.id = h2.id
JOIN hierarchy h5 ON cc.id = h5.parentid
JOIN objectnamegroup ong ON h5.id = ong.id
JOIN hierarchy h6 ON (cc.id = h6.parentid AND h6.name = 'collectionobjects_common:titleGroupList' AND h6.pos = 0)
LEFT OUTER JOIN titlegroup tg ON h6.id = tg.id
JOIN hierarchy h7 ON (cc.id = h7.parentid AND h7.name = 'collectionobjects_common:objectProductionPersonGroupList')
JOIN objectproductionpersongroup oppg ON h7.id = oppg.id

WHERE valuationid IS NOT NULL AND va.valueamount IS NOT NULL AND co.computedcurrentlocationdisplay NOT LIKE 'VN%'

ORDER BY va.valueamount DESC

LIMIT 10;
