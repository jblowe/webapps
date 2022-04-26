--How to pull every unique Object Name from the Concept Authority
SELECT substring(refname from position('''' in refname) + 1 for char_length(refname) - position('''' in refname) - 1) AS concept, refname, h.name AS csid FROM concepts_common cc

INNER JOIN hierarchy h ON cc.id = h.id WHERE cc.refname in (SELECT DISTINCT objectname from objectnamegroup);
