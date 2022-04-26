--How to pull every unique Object Name from the Concept Authority
SELECT DISTINCT substring(objectname from position('''' in objectname) + 1 for char_length(objectname) - position('''' in objectname) - 1) as object_name FROM objectnamegroup 

ORDER BY object_name; 

