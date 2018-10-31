from flask import request

from app import api_bp, JSONAPIResponseFactory


@api_bp.route("/api/<api_version>")
def api_get_capabilities(api_version):
    if "capabilities" in request.args:
        capabilities = [
            {
                "type": "capability",
                "id": "placename",
                "attributes": {
                    "description": "",
                    "endpoints":  {
                        "resource": {
                            "url": "/api/%s/placename" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/placenames" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-parameters": {

                    },
                    "collection-parameters": {

                    },
                    "resource-attributes": [
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
                    "resource-relationships": [
                        {"name": "commune", "description": ""},
                        {"name": "localization-commune", "description": ""},
                        {"name": "linked-placenames", "description": ""},
                        {"name": "alt-labels", "description": ""},
                        {"name": "old-labels", "description": ""}
                    ]
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
                            "url": "/api/%s/commune" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/communes" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-attributes": [
                        {"name": "insee-code", "description": ""},
                        {"name": "NCCENR", "description": ""},
                        {"name": "ARTMIN", "description": ""},
                        {"name": "longlat", "description": ""}
                    ],
                    "resource-relationships": [
                        {"name": "localized-placenames", "description": ""},
                        {"name": "placename", "description": ""},
                        {"name": "region", "description": ""},
                        {"name": "departement", "description": ""},
                        {"name": "arrondissement", "description": ""},
                        {"name": "canton", "description": ""}
                    ]
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
                            "url": "/api/%s/feature-type" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/feature-types" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-attributes": [
                        {"name": "term", "description": ""},
                    ],
                    "resource-relationships": [
                        {"name": "placename", "description": ""},
                    ]
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
                            "url": "/api/%s/insee-ref" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/insee-refs" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-attributes": [
                        {"name": "id", "description": ""},
                        {"name": "reference-type", "description": ""},
                        {"name": "insee-code", "description": ""},
                        {"name": "level", "description": ""},
                        {"name": "label", "description": ""},
                    ],
                    "resource-relationships": [
                        {"name": "parent", "description": ""},
                        {"name": "children", "description": ""},
                    ]
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
                            "url": "/api/%s/placename-old-label" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/placename-old-labels" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-attributes": [
                        {"name": "rich-label", "description": ""},
                        {"name": "rich-date", "description": ""},
                        {"name": "text-date", "description": ""},
                        {"name": "rich-reference", "description": ""},
                        {"name": "rich-label-node", "description": ""},
                        {"name": "text-label-node", "description": ""},
                    ],
                    "resource-relationships": [
                        {"name": "placename", "description": ""},
                        {"name": "commune", "description": ""},
                        {"name": "localization-commune", "description": ""},
                    ]
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
                            "url": "/api/%s/placename-alt-label" % api_version,
                            "parameters": {}
                        },
                        "collection": {
                            "url": "/api/%s/placename-alt-labels" % api_version,
                            "parameters": {}
                        }
                    },
                    "resource-attributes": [
                        {"name": "label", "description": ""},
                    ],
                    "resource-relationships": [
                        {"name": "placename", "description": ""},
                    ]
                },
                "usage": []
            },
        ]

        meta = {
            "description": ""
        }
        return JSONAPIResponseFactory.make_data_response(capabilities, links=None,  included_resources=None, meta=meta)