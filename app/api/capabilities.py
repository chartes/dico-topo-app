from flask import request, current_app

from app import api_bp, JSONAPIResponseFactory


@api_bp.route("/api/<api_version>")
def api_get_capabilities(api_version):
    if "capabilities" in request.args:
        url_prefix = request.host_url[:-1] + current_app.config["API_URL_PREFIX"]
        capabilities = [
            {
                "type": "capability",
                "id": "placename",
                "attributes": {
                    "description": "Toponyme",
                    "endpoints":  {
                        "resource": {
                            "url": "%s/placename/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "id", "description": "Identifiant unique du lieu"},
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
                                {"name": "commune", "description": "La reslation est renseignée si le lieu lui-même correspond à une commune", "type": "resource"},
                                {"name": "localization-commune", "description": "La relation est renseignée si le lieu peut être attaché à une commune", "type": "resource" },
                                {"name": "linked-placenames", "description": "Lieux attachés", "type": "collection"},
                                {"name": "alt-labels", "description": "Formes alternatives du toponyme", "type": "collection"},
                                {"name": "old-labels", "description": "Formes anciennes du toponyme", "type": "collection"}
                            ]
                        },
                        "collection": {
                            "url": "%s/placenames" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include" : "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight" : "Ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document (les relations ne sont incluses dans la réponse)."
                            }
                        }
                    },
                },
                "usage": []
            },

            {
                "type": "capability",
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
                                {"name": "localized-placenames", "description": ""},
                                {"name": "placename", "description": ""},
                                {"name": "region", "description": ""},
                                {"name": "departement", "description": ""},
                                {"name": "arrondissement", "description": ""},
                                {"name": "canton", "description": ""}
                            ]
                        },
                        "collection": {
                            "url": "%s/communes" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include" : "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight" : "ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document : les relations ne incluses."
                            }
                        }
                    }
                },
                "usage": []
            },

            {
                "type": "capability",
                "id": "feature-type",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/feature-type/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "id", "description": ""},
                                {"name": "term", "description": ""},
                            ],
                            "relationships": [
                                {"name": "placename", "description": ""},
                            ]
                        },
                        "collection": {
                            "url": "%s/feature-types" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include" : "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight" : "ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document : les relations ne incluses."
                            }
                        }
                    }
                },
                "usage": []
            },

            {
                "type": "capability",
                "id": "insee-ref",
                "attributes": {
                    "description": "",
                    "endpoints": {
                        "resource": {
                            "url": "%s/insee-ref/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "id", "description": ""},
                                {"name": "reference-type", "description": ""},
                                {"name": "insee-code", "description": ""},
                                {"name": "level", "description": ""},
                                {"name": "label", "description": ""},
                            ],
                            "relationships": [
                                {"name": "parent", "description": ""},
                                {"name": "children", "description": ""},
                            ]
                        },
                        "collection": {
                            "url": "%s/insee-refs" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include" : "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight" : "ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document : les relations ne incluses."
                            }
                        }
                    }
                },
                "usage": []
            },

            {
                "type": "capability",
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
                                {"name": "placename", "description": ""},
                                {"name": "commune", "description": ""},
                                {"name": "localization-commune", "description": ""},
                            ]
                        },
                        "collection": {
                            "url": "%s/placename-old-labels" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include" : "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight" : "ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document : les relations ne incluses."
                            }
                        }
                    }
                },
                "usage": []
            },

            {
                "type": "capability",
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
                                {"name": "placename", "description": ""},
                            ]
                        },
                        "collection": {
                            "url": "%s/placename-alt-labels" % url_prefix,
                            "parameters": {
                                "search": "search[fieldname1,fieldname2]=expression ou search=expression pour chercher parmis tous les champs indexés",
                                "filter": "filter[field_name]=searched_value. Le nom du champs DOIT être un des champs du model",
                                "sort": "sort=field1,field2,field3. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
                                "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
                                "include": "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
                                "lightweight": "ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document : les relations ne incluses."
                            }
                        }
                    }
                },
                "usage": []
            },
        ]

        meta = {
            "description": ""
        }
        return JSONAPIResponseFactory.make_data_response(capabilities, links=None,  included_resources=None, meta=meta)