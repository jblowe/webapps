-- nb: this query assume it will take a variety of field content: refnames, messy free text, and output something "clean"
SELECT DISTINCT cc.id AS id,
  case when cocbd.item is null or cocbd.item = '' then null else cocbd.item end as briefdescription_s

FROM collectionobjects_common cc
JOIN misc m on (m.id = cc.id AND m.lifecyclestate <> 'deleted')
LEFT OUTER JOIN collectionobjects_common_briefdescriptions cocbd on (cc.id = cocbd.id and cocbd.pos = 0)
