import json
from flask import Response


class JSONAPIResponseFactory:

    CONTENT_TYPE = "application/vnd.api+json; charset=utf-8"
    HEADERS = {"Access-Control-Allow-Origin": "*",
               "Access-Control-Allow-Methods": ["GET", "POST", "DELETE", "PATCH"]}

    @classmethod
    def encapsulate(cls, toplevel, resource, links=None, included_resources=None):
        document = {
            toplevel: resource,
            "meta": {

            },
            "jsonapi": {
                "version": "1.0"
            }
        }
        if links is not None:
            document["links"] = links
        if included_resources is not None:
            document["included"] = included_resources
        return document

    @classmethod
    def encapsulate_data(cls, resource, links, included_resources):
        return JSONAPIResponseFactory.encapsulate("data", resource, links, included_resources)

    @classmethod
    def encapsulate_errors(cls, resource, links):
        return JSONAPIResponseFactory.encapsulate("errors", resource, links)

    @classmethod
    def make_response(cls, resource, **kwargs):
        return Response(
            json.dumps(resource, indent=2, ensure_ascii=False),
            content_type=JSONAPIResponseFactory.CONTENT_TYPE,
            headers=JSONAPIResponseFactory.HEADERS,
            **kwargs
        )

    @classmethod
    def make_data_response(cls, data_resource, links, included_resources, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_data(data_resource, links, included_resources)
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

    @classmethod
    def make_errors_response(cls, errors_resource, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_errors(errors_resource, kwargs.get("links", None))
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

