
DROP TABLE IF EXISTS public.netxview;

CREATE TABLE public.netxview (
    accession_number text,
    object_name text,
    taxon text,
    object_title text,
    prod_date text,
    materials text,
    prod_technique text,
    dimensions text,
    phys_desc text,
    -- content_desc text,
    brief_desc text,
    obj_prod_org text,
    obj_prod_date text,
    -- obj_prod_person text,
    content_concepts text,
    -- content_persons text,
    assoc_persons text,
    -- content_orgs text,
    assoc_orgs text,
    -- content_place text,
    assoc_place text,
    -- object_prod_place text,
    -- field_coll_place text,
    cult_context text,
    exhibitions text,
    ip_status text,
    credit_line text,
    moddate date,
    copyrightholder_s text,
    referencenote_s text
);

CREATE INDEX idx_netxview_accession_number ON public.netxview USING btree (accession_number);
CREATE INDEX idx_netxview_moddate ON public.netxview USING btree (moddate);

