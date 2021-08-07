SELECT
    co.objectnumber objectNumber,
    co.physicalDescription physicalDescription,
    substring(co.computedcurrentlocation, position(')''' in co.computedcurrentlocation)+2, length(co.computedcurrentlocation)-position(')''' in co.computedcurrentlocation)-2) AS computedcurrentlocation,
    
    --bd.item briefDescription,
    array_to_string(array_agg(DISTINCT bd.item),', ') AS briefDescription,

    --rd.item responsibleDepartment,
    array_to_string(array_agg(DISTINCT substring(rd.item, position(')''' in rd.item)+2, length(rd.item)-position(')''' in rd.item)-2)),', ') AS responsibleDepartment,

    --cc.item contentConcept,
    array_to_string(array_agg(DISTINCT substring(cc.item, position(')''' in cc.item)+2, length(cc.item)-position(')''' in cc.item)-2)),', ') AS contentConcept,

    --cp.item contentPerson,
    array_to_string(array_agg(DISTINCT substring(cp.item, position(')''' in cp.item)+2, length(cp.item)-position(')''' in cp.item)-2)),', ') AS contentPerson,

    --corg.item contentOrganization,
    array_to_string(array_agg(DISTINCT substring(corg.item, position(')''' in corg.item)+2, length(corg.item)-position(')''' in corg.item)-2)),', ') AS contentOrganization,

    --cpl.item contentPlace,
    array_to_string(array_agg(DISTINCT substring(cpl.item, position(')''' in cpl.item)+2, length(cpl.item)-position(')''' in cpl.item)-2)),', ') AS contentPlace,

    --tg.title objectTitle,
    array_to_string(array_agg(DISTINCT tg.title),', ') AS objectTitle,

    --sd.datedisplaydate objectProductionDate,
    array_to_string(array_agg(DISTINCT sd.datedisplaydate),', ') AS objectProductionDate,

    --mpg.dimensionSummary dimensionSummary,
    array_to_string(array_agg(DISTINCT mpg.dimensionSummary),', ') AS dimensionSummary,

    --oppg.objectProductionPerson maker,
    array_to_string(array_agg(DISTINCT substring(oppg.objectProductionPerson, position(')''' in oppg.objectProductionPerson)+2, length(oppg.objectProductionPerson)-position(')''' in oppg.objectProductionPerson)-2)),', ') AS maker,

    --ong.objectName objectName,
    array_to_string(array_agg(DISTINCT substring(ong.objectName, position(')''' in ong.objectName)+2, length(ong.objectName)-position(')''' in ong.objectName)-2)),', ') AS objectName,

    --mg.material material,
    array_to_string(array_agg(DISTINCT substring(mg.material, position(')''' in mg.material)+2, length(mg.material)-position(')''' in mg.material)-2)),', ') AS material,
    
    comca.argusRemarks argusRemarks,
    comca.sortableobjectnumber sort,

    -- creditline; sortby acquisitionreferencenumber
    (SELECT string_agg(acq.creditline,', ')
        FROM relations_common racq
        LEFT OUTER JOIN hierarchy hacq ON (hacq.name = racq.objectcsid)
        LEFT OUTER JOIN acquisitions_common acq ON (hacq.id = acq.id)
        LEFT OUTER JOIN misc ON (misc.id = acq.id)
        WHERE h1.name = racq.subjectcsid AND racq.objectdocumenttype = 'Acquisition' AND misc.lifecyclestate <> 'deleted'
        GROUP BY acq.acquisitionreferencenumber
        ORDER BY acq.acquisitionreferencenumber DESC
        LIMIT 1
    ) as creditline

FROM collectionobjects_common co

    JOIN hierarchy h1 ON (co.id = h1.id)

    -- briefDescription
    LEFT OUTER JOIN collectionobjects_common_briefdescriptions bd ON (co.id = bd.id)

    -- responsibleDepartment
    LEFT OUTER JOIN collectionobjects_common_responsibledepartments rd ON (co.id = rd.id)

    -- contentConcept
    LEFT OUTER JOIN collectionobjects_common_contentconcepts cc ON (co.id = cc.id)

    -- contentPerson
    LEFT OUTER JOIN collectionobjects_common_contentpersons cp ON (co.id = cp.id)

    -- contentOrganization
    LEFT OUTER JOIN collectionobjects_common_contentorganizations corg ON (co.id = corg.id)

    -- contentPlace
    LEFT OUTER JOIN collectionobjects_common_contentplaces cpl ON (co.id = cpl.id)

    -- objectTitle
    LEFT OUTER JOIN hierarchy h2 ON (co.id = h2.parentid AND h2.name = 'collectionobjects_common:titleGroupList')
    LEFT OUTER JOIN titleGroup tg ON (h2.id = tg.id)

    -- objectProductionDate
    LEFT OUTER JOIN hierarchy h3 ON (co.id = h3.parentid AND h3.name = 'collectionobjects_common:objectProductionDateGroupList')
    LEFT OUTER JOIN structureddategroup sd ON (h3.id = sd.id)

    -- dimensionSummary
    LEFT OUTER JOIN hierarchy h4 ON (co.id = h4.parentid AND h4.name = 'collectionobjects_common:measuredPartGroupList')
    LEFT OUTER JOIN measuredpartgroup mpg ON (h4.id = mpg.id)

    -- maker
    LEFT OUTER JOIN hierarchy h5 ON (co.id = h5.parentid AND h5.name = 'collectionobjects_common:objectProductionPersonGroupList')
    LEFT OUTER JOIN objectProductionPersonGroup oppg ON (h5.id = oppg.id)

    -- objectName
    LEFT OUTER JOIN hierarchy h6 ON (co.id = h6.parentid AND h6.primarytype='objectNameGroup')
    LEFT OUTER JOIN objectnamegroup ong ON (ong.id=h6.id)

    -- material
    LEFT OUTER JOIN hierarchy h7 ON (co.id = h7.parentid AND h7.primarytype='materialGroup')
    LEFT OUTER JOIN materialgroup mg ON (mg.id=h7.id)

    INNER JOIN misc ON (misc.id = co.id AND misc.lifecyclestate <> 'deleted')
    INNER JOIN collectionspace_core core ON (core.id = co.id)
    INNER JOIN collectionobjects_omca comca ON (co.id = comca.id)

WHERE computedcurrentlocation ILIKE CONCAT('%', :v, '%')

GROUP BY objectNumber, physicalDescription, computedcurrentlocation, argusRemarks, sort, h1.name

ORDER BY sort, objectnumber ASC 
