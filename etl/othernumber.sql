SELECT x.id AS id, regexp_replace(x.numbervalue, E'[\\t\\n\\r]+', ' ', 'g') AS othernumber_s
FROM othernumber x
WHERE x.numbervalue IS NOT NULL
