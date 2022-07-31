COPY netxview
(
object_name,accession_number,taxon,phys_desc,content_desc,field_coll_place,ip_status,
moddate,cult_context,assoc_orgs,assoc_persons,assoc_place,materials,obj_prod_org,
obj_prod_person,object_prod_place,object_title,prod_technique,content_concepts,
content_place,content_persons,content_orgs,exhibitions,dimensions,credit_line,prod_date
)
FROM '/Users/johnlowe/webapps/etc/dss2022/netxview.csv'
DELIMITER ','
CSV HEADER

