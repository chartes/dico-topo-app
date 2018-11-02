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
                    "description": "",
                    "endpoints":  {
                        "resource": {
                            "url": "%s/placename/<id>" % url_prefix,
                            "parameters": {},
                            "attributes": [
                                {"name": "id", "description": ""},
                                {"name": "label", "description": ""},
                                {"name": "country", "description": ""},
                                {"name": "dpt", "description": ""},
                                {"name": "desc", "description": ""},
                                {"name": "num-start-page", "description": ""},
                                {"name": "localization-certainty", "description": ""},
                                {"name": "localization-insee-code", "description": ""},
                                {"name": "comment", "description": ""},
                            ],
                            "relationships": [
                                {"name": "commune", "description": ""},
                                {"name": "localization-commune", "description": ""},
                                {"name": "linked-placenames", "description": ""},
                                {"name": "alt-labels", "description": ""},
                                {"name": "old-labels", "description": ""}
                            ]
                        },
                        "collection": {
                            "url": "%s/placenames" % url_prefix,
                            "parameters": {}
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
                            "parameters": {}
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
                            "parameters": {}
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
                            "parameters": {}
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
                            "parameters": {}
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
                            "parameters": {}
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