from flask import request, current_app

from app import api_bp, JSONAPIResponseFactory


@api_bp.route("/api/<api_version>")
def api_get_capabilities(api_version):
    if "capabilities" in request.args:
        host = request.host_url[:-1]
        if "localhost" not in host:
            url_prefix = host + current_app.config["API_URL_PREFIX"]
            url_prefix = url_prefix.replace('http://', 'https://')
        else:
            url_prefix = "http://localhost:5003/api/1.0"

        capabilities = [
            {
                "type": "parameter",
                "id": "parameters.filter",
                "attributes": {
                    "item-kind": "collection",
                    "name": "filter",
                    "description": "filter[field_name]=searched_value"
                }

            },
            {
                "type": "parameter",
                "id": "parameters.sort",
                "attributes": {
                    "item-kind": "collection",
                    "name": "sort",
                    "description": "sort=field1,field2. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant"
                }

            },
            {
                "type": "parameter",
                "id": "parameters.page",
                "attributes": {
                    "item-kind": "collection",
                    "name": "page",
                    "description": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite côté serveur. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens."
                }

            },
            {
                "type": "parameter",
                "id": "parameters.include",
                "attributes": {
                    "item-kind": "collection, resource",
                    "name": "include",
                    "description": "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource."
                }

            },
            {
                "type": "parameter",
                "id": "parameters.without-relationships",
                "attributes": {
                    "item-kind": "collection, resource",
                    "name": "without-relationships",
                    "description": "Ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document (les relations ne sont pas incluses dans la réponse)."
                }
            },
            {
                "type": "feature",
                "id": "elasticsearch-api",
                "attributes": {
                    "title": "Rercherche avancée",
                    "content": "L'application expose un point d'entrée vers un moteur de recherche Elasticsearch. Les requêtes retournant plus de 10.000 résultats ne seront pas exécutées.",
                    "examples": [
                        {
                            "description": "Recherche du terme 'Poizatière'",
                            "content": f"{url_prefix}/search?query=label.folded:Poizatière&sort=place-label.keyword&page[size]=200&page[number]=1"
                        }
                    ]
                }
            },
            {
                "type": "feature",
                "id": "export-linked-places",
                "attributes": {
                    "title": "Export Linked Places",
                    "content": "L'API permet d'exporter les lieux identifiés au format Linked Places",
                    "examples": [
                        {
                            "description": "Export d'un lieu",
                            "content": f"{url_prefix}/places/P41693029?export=linkedplaces"
                        },
                        {
                            "description": "Export d'une collection de lieux",
                            "content": f"{url_prefix}/search?query=label.folded:Troyes&export=linkedplaces"
                        }
                    ]
                }
            },
            {
                "type": "resource",
                "id": "place",
                "attributes": {
                    "description": "Lieu",
                    "endpoints":  {
                        "resource": {
                            "url": f"{url_prefix}/place/<id>",
                            "parameters": {},
                            "attributes": [
                                {"name": "label", "description": "Vedette de l'article telle que présente dans l'ouvrage d'origine "},
                                {"name": "country", "description": "Pays"},
                                {"name": "dpt", "description": "Département"},
                                {"name": "num-start-page", "description": "Numéro de la première page du tome d'origine où est inscrit le toponyme"},
                                {"name": "localization-insee-code", "description": "Code insee de la commune attachée (si connue)"},
                                {"name": "localization-commune-relation-type",
                                 "description": "Type de relation entre ce lieu et son éventuelle commune associée"},

                                {"name": "geoname-id", "description": ""},
                                {"name": "wikidata-item-id", "description": ""},
                                {"name": "wikipedia-url", "description": ""},
                                {"name": "databnf-ark", "description": ""},
                                {"name": "viaf-id", "description": ""},
                                {"name": "siaf-id", "description": ""},
                                {"name": "osm-id", "description": ""},
                                {"name": "inha-uuid", "description": ""},
                            ],
                            "relationships": [
                                {"name": "responsibility",
                                 "description": "Mention de responsabilité de la notice",
                                 "type": "resource",
                                 "ref": "responsibility"},
                                {"name": "commune", "description": "La relation est renseignée si le lieu lui-même correspond à une commune", "type": "resource",
                                 "ref": "commune"},
                                {"name": "localization-commune", "description": "La relation est renseignée si le lieu peut être attaché à une commune", "type": "resource",
                                 "ref": "commune"},
                                {"name": "descriptions", "description": "Descriptions du lieu"},
                                {"name": "comments",
                                 "description": "Commentaires apportés tant au niveau du lieu que des ressources liées"},
                                {"name": "linked-places", "description": "Lieux attachés", "type": "collection",
                                 "ref": "place"},
                                {"name": "old-labels", "description": "Formes anciennes du toponyme", "type": "collection", "ref": "place-old-label"},

                            ]
                        },
                        "collection": {
                            "url": f"{url_prefix}/places?page[size]=3",

                        }
                    },
                    "examples": {
                        "url": f"{url_prefix}/places/P61132243"
                    }
                },

            },

            {
                "type": "resource",
                "id": "commune",
                "attributes": {
                    "description": "",
                    "endpoints":  {
                        "resource": {
                            "url": f"{url_prefix}/commune/<insee-code>",
                            "parameters": {},
                            "attributes": [
                                {"name": "insee-code", "description": ""},
                                {"name": "place-id", "description": ""},
                                {"name": "NCCENR", "description": ""},
                                {"name": "ARTMIN", "description": ""},
                                {"name": "longlat", "description": ""},

                                {"name": "geoname-id", "description": ""},
                                {"name": "wikidata-item-id", "description": ""},
                                {"name": "wikipedia-url", "description": ""},
                                {"name": "databnf-ark", "description": ""},
                                {"name": "viaf-id", "description": ""},
                                {"name": "siaf-id", "description": ""},
                                {"name": "osm-id", "description": ""},
                                {"name": "inha-uuid", "description": ""},
                            ],
                            "relationships": [
                                {"name": "localized-places", "description": "",
                                 "type": "collection", "ref": "place"},
                                {"name": "place", "description": "",
                                 "type": "resource", "ref": "place"},
                                {"name": "region", "description": "",
                                 "type": "resource", "ref": "insee-ref"},
                                {"name": "departement", "description": "",
                                 "type": "resource", "ref": "insee-ref"},
                                {"name": "arrondissement", "description": "",
                                 "type": "resource", "ref": "insee-ref"},
                                {"name": "canton", "description": "",
                                 "type": "resource", "ref": "insee-ref"}
                            ]
                        },
                        "collection": {
                            "url": f"{url_prefix}/communes?page[size]=10",

                        }
                    },
                    "examples": {
                        "url": f"{url_prefix}/communes/01367"
                    }
                },

            },

            {
                "type": "resource",
                "id": "place-feature-type",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": f"{url_prefix}/place-feature-type/<id>",
                            "parameters": {},
                            "attributes": [
                                {"name": "term", "description": ""},
                            ],
                            "relationships": [
                                {"name": "place", "description": "",
                                 "type": "resource", "ref": "place"},
                                {"name": "responsibility", "description": "",
                                 "type": "resource", "ref": "responsibility"},
                            ]
                        },
                        "collection": {
                            "url": f"{url_prefix}/place-feature-types?page[size]=10",

                        }
                    },
                    "examples": {
                        "url": f"{url_prefix}/place-feature-types/124"
                    }
                },

            },

            {
                "type": "resource",
                "id": "insee-ref",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": f"{url_prefix}/insee-ref/<id>",
                            "parameters": {},
                            "attributes": [
                                {"name": "reference-type", "description": ""},
                                {"name": "insee-code", "description": ""},
                                {"name": "level", "description": ""},
                                {"name": "label", "description": ""},
                            ],
                            "relationships": [
                                {"name": "parent", "description": "",
                                 "type": "resource", "ref": "insee-ref"},
                                {"name": "children", "description": "",
                                 "type": "collection", "ref": "insee-ref"},
                            ]
                        },
                        "collection": {
                            "url": f"{url_prefix}/insee-refs?page[size]=10",

                        }
                    },
                    "examples": {
                        "url": f"{url_prefix}/insee-refs/DEP_03"
                    }
                },

            },

            {
                "type": "resource",
                "id": "place-old-label",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/place-old-label/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "rich-label", "description": ""},
                                {"name": "rich-date", "description": ""},
                                {"name": "text-date", "description": ""},
                                {"name": "rich-reference", "description": ""},
                            ],
                            "relationships": [
                                {"name": "place", "description": "",
                                 "type": "resource", "ref": "place"},
                                {"name": "commune", "description": "",
                                 "type": "resource", "ref": "commune"},
                                {"name": "localization-commune", "description": "",
                                 "type": "resource", "ref": "commune"},
                                {"name": "responsibility", "description": "",
                                 "type": "resource", "ref": "responsibility"},
                            ]
                        },
                        "collection": {
                            "url": "%s/place-old-labels?page[size]=10" % url_prefix,

                        }
                    },
                    "examples": {
                        "url": "%s/place-old-labels/93" % url_prefix
                    }
                },

            }
        ]

        meta = {
            "description": ""
        }
        return JSONAPIResponseFactory.make_data_response(capabilities, links=None,  included_resources=None, meta=meta)
