select h.name, p.id,p.refname,m.lifecyclestate from places_common p
   join hierarchy h on (p.id = h.id)
   join misc m on (p.id = m.id)
