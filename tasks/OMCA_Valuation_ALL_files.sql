SELECT
    vcc.valuationcontrolrefnumber valuationcontrolrefnumber,
    va.valuecurrency valuecurrency,
    va.valueamount valueamount,
    vcc.valuetype valuetype,
    vcc.valuedate valuedate,
    vcc.valuesource valuesource,
    vcc.valuenote valuenote,
    co.objectnumber objectNumber,
    comca.sortableobjectnumber sort

FROM
    valuationcontrols_common vcc

    -- valueamount
    LEFT OUTER JOIN hierarchy h2 ON (vcc.id = h2.parentid AND h2.name='valuationcontrols_common:valueAmountsList')
    LEFT OUTER JOIN valueamounts va ON (h2.id = va.id)

    -- Get related Cataloging records
    LEFT OUTER JOIN hierarchy hrel ON (vcc.id = hrel.id)
    LEFT OUTER JOIN relations_common r1 ON (r1.subjectcsid = hrel.name AND r1.objectdocumenttype = 'CollectionObject')
    LEFT OUTER JOIN hierarchy hco ON (r1.objectcsid = hco.name)
    LEFT OUTER JOIN collectionobjects_common co ON (co.id = hco.id)
    LEFT OUTER JOIN collectionobjects_omca comca ON (co.id = comca.id)

    INNER JOIN misc ON (misc.id = vcc.id AND misc.lifecyclestate <> 'deleted')
    INNER JOIN collectionspace_core core ON core.id = vcc.id

ORDER BY sort, valuedate ASC;
