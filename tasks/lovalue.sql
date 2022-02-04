SELECT
    gc.loanoutnumber grouptitle,
    CASE WHEN (gc.borrower IS NOT NULL AND gc.borrower <> '') THEN
        regexp_replace(gc.borrower, '^.*\)''(.*)''$', '\1')
        ELSE ''
    END AS groupOwner,
    gc.loanoutnote scopenote,
    co.id objectid,
    co.objectnumber objectnumber,
    comca.sortableobjectnumber sortableobjectnumber,
    h2.name objcsid,
    comca.argusDescription argusDescription,

    --sd.datedisplaydate objectProductionDate,
    array_to_string(array_agg(DISTINCT (h3.pos, sd.datedisplaydate)),';;') AS objectProductionDate,

    --mpg.dimensionSummary dimensionSummary,
    array_to_string(array_agg(DISTINCT (h4.pos, mpg.dimensionSummary)),';;') AS dimensionSummary,

    --tg.title objectTitle,
    array_to_string(array_agg(DISTINCT (h5.pos, tg.title)),';;') AS objectTitle,

    -- creditline; sortby acquisitionreferencenumber
    (SELECT string_agg(acq.creditline,' ' ORDER BY acq.acquisitionreferencenumber)
        FROM relations_common racq
        LEFT OUTER JOIN hierarchy hacq ON (hacq.name = racq.objectcsid)
        LEFT OUTER JOIN acquisitions_common acq ON (hacq.id = acq.id)
        LEFT OUTER JOIN misc ON (misc.id = acq.id)
        WHERE h2.name = racq.subjectcsid AND racq.objectdocumenttype = 'Acquisition' AND misc.lifecyclestate <> 'deleted'
        GROUP BY acq.acquisitionreferencenumber
        ORDER BY acq.acquisitionreferencenumber DESC
        LIMIT 1
    ) AS creditline,

    (SELECT va.valueamount
      -- rc.subjectcsid
      FROM relations_common rc
      LEFT JOIN hierarchy hrc2 ON (hrc2.name = rc.subjectcsid)
      JOIN valuationcontrols_common vc ON (hrc2.id = vc.id)

      LEFT JOIN hierarchy hrc4 ON hrc4.parentid = hrc2.id
      LEFT JOIN valueamounts va ON hrc4.id = va.id
      WHERE rc.objectcsid = h2.name AND rc.subjectdocumenttype = 'Valuationcontrol' AND vc.valuedate IS NOT NULL
      ORDER BY vc.valuedate DESC
      LIMIT 1
    ) AS valuationid,

    -- blobCSID from Media
    (SELECT med.blobCsid
        FROM relations_common rmed
        LEFT OUTER JOIN hierarchy hmed ON (hmed.name = rmed.objectcsid)
        LEFT OUTER JOIN media_common med ON (hmed.id = med.id)
        LEFT OUTER JOIN media_omca momca ON (med.id = momca.id)
        LEFT OUTER JOIN misc ON (misc.id = med.id)
        WHERE h2.name = rmed.subjectcsid AND rmed.objectdocumenttype = 'Media' AND momca.isPrimary = 'True' AND misc.lifecyclestate <> 'deleted'
        ORDER BY med.identificationNumber DESC
        LIMIT 1
    ) AS blobCSID

FROM loansout_common gc

    JOIN hierarchy h1 ON (gc.id=h1.id)
    JOIN relations_common rc1 ON (h1.name=rc1.subjectcsid)

    JOIN hierarchy h2 ON (rc1.objectcsid=h2.name)
    JOIN collectionobjects_common co ON (h2.id=co.id)

    -- objectProductionDate
    LEFT OUTER JOIN hierarchy h3 ON (co.id = h3.parentid AND h3.name = 'collectionobjects_common:objectProductionDateGroupList')
    LEFT OUTER JOIN structureddategroup sd ON (h3.id = sd.id)

    -- dimensionSummary
    LEFT OUTER JOIN hierarchy h4 ON (co.id = h4.parentid AND h4.name = 'collectionobjects_common:measuredPartGroupList')
    LEFT OUTER JOIN measuredpartgroup mpg ON (h4.id = mpg.id)
    
    -- objectTitle
    LEFT OUTER JOIN hierarchy h5 ON (co.id = h5.parentid AND h5.name = 'collectionobjects_common:titleGroupList')
    LEFT OUTER JOIN titleGroup tg ON (h5.id = tg.id)

    INNER JOIN misc ON (misc.id = co.id AND misc.lifecyclestate <> 'deleted')
    INNER JOIN collectionspace_core core ON (core.id = co.id)
    INNER JOIN collectionobjects_omca comca ON (co.id = comca.id)

WHERE h1.name='ec7dce05-e095-43df-9668'

GROUP BY grouptitle, groupOwner, scopenote, objectid, objectnumber, sortableobjectnumber, objcsid, argusDescription

ORDER BY comca.sortableobjectnumber
