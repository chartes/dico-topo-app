Linked-Places serialization
===

## Mapping
DT API (dev) : https://dev.chartes.psl.eu/dico-topo/api/1.0/placenames/DT02-01486?include=old-labels,commune,localization-commune,linked-placenames


|[Linked Places](https://github.com/LinkedPasts/linked-places)|[DicoTopo API](https://dev.chartes.psl.eu/dico-topo/api/1.0/placenames/DT02-01486?include=old-labels,commune,localization-commune,linked-placenames)|Comments|
|---|---|---|
|`$.features.@id`|`$.data.links.self`|String processing required for conversion if link to [page](https://dev.chartes.psl.eu/dico-topo/placenames/DT02-01486) and not to the resource (API).|
|`$.features.properties.title`|`$.data.attributes.label`||
|`$.features.properties.ccode`|`$.data.attributes.country`||
|`$.features.geometry.geometries[?(@.type='Point')].coordinates`|`$.included[?(@.type='commune')].attributes.longlat`|(long,lat); string processing required.<br/>**NB**. Need to include both `commune` and `localization-commune` relationships to get the data.<br/>TODO. Perhaps redefine DT API (distinction `commune`/`localization-commune` unclear – but useful for `relations[]`).|
|`$.features.geometry.geometries[?(@.type='Point')].geo_wkt`|`$.included[?(@.type='commune')].attributes.longlat`|*Idem*.|
|`$.features.geometry.geometries[?(@.type='Point')].when.timespans.start.in`|`2011`|Coordinate pair, [GEOFLA 2011 (IGN)](http://professionnels.ign.fr/adminexpress).|
|`$.features.geometry.geometries[?(@.type='Point')].when.timespans.end.in`|`2011`|*Idem*.|
|`$.features.geometry.geometries[?(@.type='Point')].src`|`$.data.attributes.localization-insee-code`|String processing required to build URL.<br/>Choice :<ul><li>http://id.insee.fr/geo/commune/02196 : insee ref, but geometry unavailable;</li><li>https://geo.api.gouv.fr/communes/02196?fields=centre : real src, but not permalink;</li><li>build `insee:insee-code` (eg `insee:02196`)?</li></ul>|
|`$.features.when.timespans.start`|`$.included.attributes.text-date[0]`|First occurence in our gazetteer? Processing required: sort dates.|
|`$.features.when.timespans.end`|?|Last occurrence of current place? Today? Date of publication of the Dictionary (1871)?|
|`$.features.names.toponym`|`$.included[?(@.type='placename-old-label')].attributes.rich-label`|Processing required to remove tags.|
|`$.features.names.lang`|not available|Required? Not easy to define in our case.|
|`$.features.names.citation.@id`|?|Required? We have the toponym reference (bibl) but no identifier (or URI) for this reference, [eg](https://dev.chartes.psl.eu/dico-topo/api/1.0/placename-old-labels/2943).|
|`$.features.types.identifier`|not available (yet)|Linking to a published vocabulary seems difficult. Can we link to our own vocabulary? We still have to standardize its items – we'll need to discuss that point with a proposal.<br/>TODO: processing to extract feature type + API refactoring.|
|`$.features.types.label`|`$.data.desc` ?|TODO: add feature-types relationship to placenames endpoint.|
|`$.features.types.sourceLabel`|?|?|
|`$.features.types.when`|?|If the type of the place changes over time?|
|`$.features.relations.relationType`|[`"gvp:broaderPartitive"`](http://vocab.getty.edu/ontology#broaderPartitive)<br/><br/>`"gvp:tgn3000_related_to"`?|`gvp:broaderPartitive`. Only the parent? For Clacy, we can rebuild: Clacy < canton de Laon-1 (`canton`) < arrondissement de Laon (`arrondissement`) < canton Aisne (`département`) < Picardie (`région`) < France (`pays`)<br/><ul><li>For `commune` (town) : easy to get the `département` (probably the most valuable data for disambiguating).</li><li>For inframunicipal place : easy to get (1) the `commune` and (2) the `département`.</li></ul>`gvp:tgn3000_related_to`? **We can also express the attachment of sub-communal toponyms to a municipality. What would be the right generic relationship** (impossible to deal with on a case-by-case basis)? For [example](https://dev.chartes.psl.eu/dico-topo/placenames/DT02-01486):<ul><li>Aulnois, mill and farm, commune of Clacy; destroyed.</li><li>Boisencourt, in the vicinity of Clacy.</li><li>Fonberlieu, wood, commune of Clacy.</li></ul>|
|`$.features.relations.relationTo `|(a) Département: `$data.attributes.dpt`<br/>(b) Sub-communal toponyms: `$included[?(@.type='placename')].links.self`|(a) Département: do we need to declare a URI for each administrative entity? Or can we link to another source such as IGN or wikidata?|
|`$.features.relations.label`|(a) Département: DB<br/>(b) Sub-communal toponyms: `$included[?(@.type='placename')].attributes.label`|TODO: provide the ability to build this label (`Commune de…`, `Département de…`, `Région…`).|
|`$.features.relations.when.start`|(a) Département: not available<br/>(b) Sub-communal toponyms: date of publication of the dictionary? (Its author establishes the relationship).|(a) Département, TODO: get the year of creation of each French *département* and *région* and store the data.|
|`$.features.relations.when.end`|none|Can we omit it? (see json example below).|
|`$features.links`|not available|**TODO (top priority)**: link insee codes with GeoNames URIs.|
|`$features.descriptions.@id`|URL of DT entity ?|Pocessing required. See json example below: correct semantics?|
|`$features.descriptions.value`|`$data.attributes.desc`| See json example below: correct semantics?|
|`$features.descriptions.lang`|`"fr"`||
|`$features.depictions`|not available||


## `DT02-01486_lp.json` (Clacy)
Test: https://gist.github.com/architexte/2dc3e1be869427b74fe0623a7a1686ae

```json
{
  "type": "FeatureCollection",
  "@context": "http://linkedpasts.org/assets/linkedplaces-context-v1.3.jsonld",
  "features": [
    { "@id": "https://dev.chartes.psl.eu/dico-topo/placenames/DT02-01486",
      "type": "Feature",
      "properties":{
        "title": "Clacy",
        "ccode": "FR"
      },
      "geometry": {
        "type": "GeometryCollection",
        "geometries": [
            { "type": "Point",
              "coordinates": [3.5654677192982454,49.55239526315789],
              "geo_wkt": "POINT(3.5654677192982454 49.55239526315789)",
              "when": {"timespans":[
                {"start":{"in":"2011"},"end":{"in":"2011"}}]},
              "src": "http://id.insee.fr/geo/commune/02196"
            }
        ]
      },
      "when": {
        "timespans": [
          {
            "start": {"in":"1122"},"end": {"in":"1871"}
          }
        ]
      },
      "names": [
        { "toponym":"Claciacum",
          "lang":"la",
          "citation": {
            "label": "cart. de l’abb. de Saint-Martin de Laon, f° 172, bibl. de Laon",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1122"},
                "end": {"in":"1122"}
              }]
          }
        },
        { "toponym":"Claci",
          "lang":"fr",
          "citation": {
            "label": "cart. de l’abb. de Saint-Martin de Laon, f° 175",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1161"},
                "end": {"in":"1161"}
              }]
          }
        },
        { "toponym":"Claceium",
          "lang":"la",
          "citation": {
            "label": "gr. cart. de l’év. de Laon, ch. 80",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1222"},
                "end": {"in":"1222"}
              }]
          }
        },
        { "toponym":"Claceyum",
          "lang":"la",
          "citation": {
            "label": "inv. de Vauclerc, Bibl. imp.",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1200~"},
                "end": {"in":"1299~"}
              }]
          }
        },
        { "toponym":"Clacci",
          "lang":"fr",
          "citation": {
            "label": "cueilleret de l’Hôtel-Dieu de Laon, B 63",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1326"},
                "end": {"in":"1326"}
              }]
          }
        },
        { "toponym":"Clacy-sous-Laon",
          "lang":"fr",
          "citation": {
            "label": "arch. de l’Emp. Tr. des chartes, reg. 64, n° 740",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1327"},
                "end": {"in":"1327"}
              }]
          }
        },
        { "toponym":"Clachy",
          "lang":"fr",
          "citation": {
            "label": "ch. de l’abb. de Saint-Vincent de Laon",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1447"},
                "end": {"in":"1447"}
              }]
          }
        },
        { "toponym":"Classy",
          "lang":"fr",
          "citation": {
            "label": "comptes de l’Hôtel-Dieu de Laon, E 25",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1493"},
                "end": {"in":"1493"}
              }]
          }
        },
        { "toponym":"Clascy, Classy-et-Thiéret",
          "lang":"fr",
          "citation": {
            "label": "acquits, arch. de la ville de Laon",
            "@id":""
          },
          "when": {
            "timespans": [{
                "start": {"in":"1568"},
                "end": {"in":"1568"}
              }]
          }
        }
      ],
      "types": [
        {
          "identifier": "dt:?",
          "label": "commune",
          "sourceLabel": "Market Town",
          "when": {"timespans":[{"start":{"in":"1600"}}]}
        }
      ],
      "relations": [
        { "relationType": "gvp:broaderPartitive",
          "relationTo": "dt:?",
          "label": "Département de l’Aisne",
          "when": {"timespans":[
            {"start":{"in":"1790"}}
          ]}
        },
        { "relationType": "gvp:tgn3000_related_to",
          "relationTo": "https://dev.chartes.psl.eu/dico-topo/placenames/DT02-00197",
          "label": "Aulnois (according to Dictionnaire topographique)",
          "when": {"timespans":[
            {"start":{"in":"1871"}}
          ]}
        },
        { "relationType": "gvp:tgn3000_related_to",
          "relationTo": "https://dev.chartes.psl.eu/dico-topo/placenames/DT02-00629",
          "label": "Boisencourt (according to Dictionnaire topographique)",
          "when": {"timespans":[
            {"start":{"in":"1871"}}
          ]}
        },
        { "relationType": "gvp:tgn3000_related_to",
          "relationTo": "https://dev.chartes.psl.eu/dico-topo/placenames/DT02-02267",
          "label": "Fonberlieu (according to Dictionnaire topographique)",
          "when": {"timespans":[
            {"start":{"in":"1871"}}
          ]}
        }
      ],
      "links": [
        {"type": "exactMatch", "identifier": "http://id.insee.fr/geo/commune/02196"},
        {"type": "exactMatch", "identifier": "http://geonames.org/6424819/"},
        {"type": "exactMatch", "identifier": "https://data.bnf.fr/ark:/12148/cb15243384f"},
        {"type": "exactMatch", "identifier": "https://www.wikidata.org/wiki/Q847885"}
      ],
      "descriptions": [
        {
          "@id": "https://dev.chartes.psl.eu/dico-topo/placenames/DT02-01486",
          "value": "Commune du canton de Laon.",
          "lang": "fr"
        }
      ],
      "depictions": [
      ]
    }
  ]
}

```
