COPY netxview
    (
     object_name, accession_number, taxon, phys_desc, ip_status,
     cult_context, assoc_persons, assoc_place,
     obj_prod_org, assoc_orgs, prod_date, materials,
     obj_prod_date, object_title, prod_technique, content_concepts,
     exhibitions, dimensions, credit_line, moddate
        )
    FROM '/Users/johnlowe/webapps/etc/dss2022/netxview.csv'
    -- FROM '/home/webapps/webapps/etc/dss2022/netxview.csv'
    DELIMITER E'\t'
    CSV HEADER
