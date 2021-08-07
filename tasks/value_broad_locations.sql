\echo MUSEUM
SELECT sum(va.valueamount) as value
FROM collectionobjects_common cc
JOIN collectionobjects_omca co ON cc.id = co.id
JOIN hierarchy h1 ON h1.id = co.id
JOIN hierarchy h2 ON h2.name = (SELECT rc.subjectcsid
                                FROM relations_common rc
                                JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
                                JOIN valuationcontrols_common vc ON (h2.id = vc.id)
                                WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol'
                                ORDER BY vc.valuedate DESC NULLS LAST
                                LIMIT 1)
JOIN hierarchy h3 ON h3.parentid = h2.id
JOIN valueamounts va ON va.id = h3.id
LEFT OUTER JOIN misc ON h1.id = misc.id

WHERE lower(co.computedcurrentlocationdisplay) LIKE 'w%' AND misc.lifecyclestate <> 'deleted';

\echo Conservation Lab
SELECT sum(va.valueamount) as value
FROM collectionobjects_common cc
JOIN collectionobjects_omca co ON cc.id = co.id
JOIN hierarchy h1 ON h1.id = co.id
JOIN hierarchy h2 ON h2.name = (SELECT rc.subjectcsid
                                FROM relations_common rc
                                JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
                                JOIN valuationcontrols_common vc ON (h2.id = vc.id)
                                WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol'
                                ORDER BY vc.valuedate DESC NULLS LAST
                                LIMIT 1)
JOIN hierarchy h3 ON h3.parentid = h2.id
JOIN valueamounts va ON va.id = h3.id
LEFT OUTER JOIN misc ON h1.id = misc.id

WHERE lower(co.computedcurrentlocationdisplay) LIKE 'omcc%' AND misc.lifecyclestate <> 'deleted';

\echo CCRC
SELECT sum(va.valueamount) as value
FROM collectionobjects_common cc
JOIN collectionobjects_omca co ON cc.id = co.id
JOIN hierarchy h1 ON h1.id = co.id
JOIN hierarchy h2 ON h2.name = (SELECT rc.subjectcsid
                                FROM relations_common rc
                                JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
                                JOIN valuationcontrols_common vc ON (h2.id = vc.id)
                                WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol'
                                ORDER BY vc.valuedate DESC NULLS LAST
                                LIMIT 1)
JOIN hierarchy h3 ON h3.parentid = h2.id
JOIN valueamounts va ON va.id = h3.id
LEFT OUTER JOIN misc ON h1.id = misc.id

WHERE lower(co.computedcurrentlocationdisplay) LIKE 'm%' AND misc.lifecyclestate <> 'deleted';

\echo Total
SELECT sum(va.valueamount) as value
FROM collectionobjects_common cc
JOIN collectionobjects_omca co ON cc.id = co.id
JOIN hierarchy h1 ON h1.id = co.id
JOIN hierarchy h2 ON h2.name = (SELECT rc.subjectcsid
                                FROM relations_common rc
                                JOIN hierarchy h2 ON (h2.name = rc.subjectcsid)
                                JOIN valuationcontrols_common vc ON (h2.id = vc.id)
                                WHERE rc.objectcsid = h1.name AND rc.subjectdocumenttype = 'Valuationcontrol'
                                ORDER BY vc.valuedate DESC NULLS LAST
                                LIMIT 1)
JOIN hierarchy h3 ON h3.parentid = h2.id
JOIN valueamounts va ON va.id = h3.id
LEFT OUTER JOIN misc ON h1.id = misc.id

WHERE misc.lifecyclestate <> 'deleted';

