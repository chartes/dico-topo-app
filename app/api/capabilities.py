from flask import request, current_app

from app import api_bp, JSONAPIResponseFactory


@api_bp.route("/api/<api_version>")
def api_get_capabilities(api_version):
    if "capabilities" in request.args:
        url_prefix = request.host_url[:-1] + current_app.config["API_URL_PREFIX"]
        capabilities = [
            {
                "type": "feature",
                "id": "db-search-api",
                "attributes": {
                    "title": "Recherche simple",
                    "content": "Il est possible d'effectuer des recherches simples sur des ressources spécifiques sans utiliser les indexes avancés d'elasticsearch",
                    "examples": [
                        {
                            "description": "Recherche du toponyme 'Metz'",
                            "content": "%s/placenames?filter[label]=Metz" % url_prefix
                        }
                    ]
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
                            "description": "Recherche du toponyme 'Metz'",
                            "content": "%s/search?query=*Metz*&index=dicotopo__development__placenames" % url_prefix
                        }
                    ]
                }
            },
            {
                "type": "resource",
                "id": "placename",
                "attributes": {
                    "description": "Toponyme",
                    "endpoints":  {
                        "resource": {
                            "url": "%s/placename/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "label", "description": "Vedette de l'article telle que présente dans l'ouvrage d'origine "},
                                {"name": "country", "description": "Pays"},
                                {"name": "dpt", "description": "Département"},
                                {"name": "desc", "description": "Description du lieu"},
                                {"name": "num-start-page", "description": "Numéro de la première page du tome d'origine où est inscrit le toponyme"},
                                {"name": "localization-certainty", "description": "Indice de confiance quant à la localisation du lieu"},
                                {"name": "localization-insee-code", "description": "Code insee de la commune attachée (si connue)"},
                                {"name": "comment", "description": "Commentaire apporté tant au niveau du lieu que des ressources liées"},
                            ],
                            "relationships": [
                                {"name": "commune", "description": "La reslation est renseignée si le lieu lui-même correspond à une commune", "type": "resource",
                                 "ref": "commune"},
                                {"name": "localization-commune", "description": "La relation est renseignée si le lieu peut être attaché à une commune", "type": "resource",
                                 "ref": "commune"},
                                {"name": "linked-placenames", "description": "Lieux attachés", "type": "collection",
                                 "ref": "placename"},
                                {"name": "alt-labels", "description": "Formes alternatives du toponyme", "type": "collection", "ref": "placename-alt-label"},
                                {"name": "old-labels", "description": "Formes anciennes du toponyme", "type": "collection", "ref": "placename-old-label"}
                            ]
                        },
                        "collection": {
                            "url": "%s/placenames?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/placenames/DT80-03029" % url_prefix
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
                            "url": "%s/commune/<insee-code>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "insee-code", "description": ""},
                                {"name": "NCCENR", "description": ""},
                                {"name": "ARTMIN", "description": ""},
                                {"name": "longlat", "description": ""}
                            ],
                            "relationships": [
                                {"name": "localized-placenames", "description": "",
                                 "type": "collection", "ref": "placename"},
                                {"name": "placename", "description": "",
                                 "type": "resource", "ref": "placename"},
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
                            "url": "%s/communes?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/communes/01025" % url_prefix
                    }
                },
                
            },

            {
                "type": "resource",
                "id": "feature-type",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/feature-type/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "term", "description": ""},
                            ],
                            "relationships": [
                                {"name": "placename", "description": "",
                                 "type": "resource", "ref": "placename"},
                            ]
                        },
                        "collection": {
                            "url": "%s/feature-types?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/feature-types/124" % url_prefix
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
                            "url": "%s/insee-ref/<id>" % url_prefix,
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
                            "url": "%s/insee-refs?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/insee-refs/DEP_03" % url_prefix
                    }
                },
                
            },

            {
                "type": "resource",
                "id": "placename-old-label",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/placename-old-label/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "rich-label", "description": ""},
                                {"name": "rich-date", "description": ""},
                                {"name": "text-date", "description": ""},
                                {"name": "rich-reference", "description": ""},
                                {"name": "rich-label-node", "description": ""},
                                {"name": "text-label-node", "description": ""},
                            ],
                            "relationships": [
                                {"name": "placename", "description": "",
                                 "type": "resource", "ref": "placename"},
                                {"name": "commune", "description": "",
                                 "type": "resource", "ref": "commune"},
                                {"name": "localization-commune", "description": "",
                                 "type": "resource", "ref": "commune"},
                            ]
                        },
                        "collection": {
                            "url": "%s/placename-old-labels?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/placename-old-labels/93" % url_prefix
                    }
                },
                
            },

            {
                "type": "resource",
                "id": "placename-alt-label",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/placename-alt-label/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "label", "description": ""},
                            ],
                            "relationships": [
                                {"name": "placename", "description": "",
                                 "type": "resource", "ref": "placename"},
                            ]
                        },
                        "collection": {
                            "url": "%s/placename-alt-labels?page[size]=10" % url_prefix,
                            
                        }
                    },
                    "examples": {
                        "url": "%s/placename-alt-labels/24" % url_prefix
                    }
                },
                
            },
        ]

        meta = {
            "description": ""
        }
        return JSONAPIResponseFactory.make_data_response(capabilities, links=None,  included_resources=None, meta=meta)