SELECT DISTINCT substring(refname from position('''' in refname) + 1 for char_length(refname) - position('''' in refname) - 1), h.name FROM AUTHORITY_common JOIN hierarchy h on h.id = AUTHORITY_common.id LEFT OUTER JOIN misc  ON h.id = misc.id WHERE misc.lifecyclestate <> 'deleted';

