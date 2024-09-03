SELECT DISTINCT cc.id AS id,
regexp_replace(
'<p>Consultation and/or research has led us to believe that this item is
not considered funerary or culturally sensitive. However, affiliated
Tribe(s) determine the cultural significance of their items. If this
item is a part of your heritage and you wish to contact us about it,
please email <a href="mailto:nagpra@museumca.org">nagpra@museumca.org</a>.
</p>
<p>For additional information on OMCA’s work in service to Native communities, please click
<a href="https://museumca.org/about-us/our-work-in-service-of-native-communities/">here</a>.</p>', E'[\\t\\n\\r]+', ' ', 'g')
    AS nagprastatement_s

FROM collectionobjects_common cc
    JOIN misc m on (m.id = cc.id AND m.lifecyclestate <> 'deleted')
WHERE cc.collection ilike '%nagpra%'
