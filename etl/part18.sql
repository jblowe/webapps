SELECT DISTINCT cc.id                                                                                                                                                    AS id,
    'Placeholder for statement. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.' AS nagprastatement_s

FROM collectionobjects_common cc
    JOIN misc m on (m.id = cc.id AND m.lifecyclestate <> 'deleted')
WHERE cc.collection ilike '%nagpra%'
