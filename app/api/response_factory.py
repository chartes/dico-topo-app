import json
from flask import Response


class JSONAPIResponseFactory:
    CONTENT_TYPE = "application/vnd.api+json; charset=utf-8"
    HEADERS = {"Access-Control-Allow-Origin": "*",
               "Access-Control-Allow-Methods": ["GET", "POST", "DELETE", "PATCH"]}

    @classmethod
    def encapsulate(cls, toplevel, resource, links=None, included_resources=None, meta=None):
        document = {
            toplevel: resource,
            "jsonapi": {
                "version": "1.0"
            }
        }
        if meta is not None:
            document["meta"] = meta
        if links is not None:
            document["links"] = links
        if included_resources is not None:
            document["included"] = included_resources
        return document

    @classmethod
    def encapsulate_data(cls, resource, links, included_resources, meta):
        return JSONAPIResponseFactory.encapsulate("data", resource, links, included_resources, meta)

    @classmethod
    def encapsulate_errors(cls, resource, links):
        return JSONAPIResponseFactory.encapsulate("errors", resource, links)

    @classmethod
    def make_response(cls, resource, **kwargs):
        headers = kwargs.get("headers", {})
        headers.update(JSONAPIResponseFactory.HEADERS)
        content_type = kwargs.get("content_type", JSONAPIResponseFactory.CONTENT_TYPE)
        raw = kwargs.get("raw")

        if "headers" in kwargs:
            kwargs.pop("headers")
        if "content_type" in kwargs:
            kwargs.pop("content_type")
        return Response(
            resource if raw else json.dumps(resource, indent=2, ensure_ascii=False),
            content_type=content_type,
            headers=headers,
            **kwargs
        )

    @classmethod
    def make_data_response(cls, data_resource, links, included_resources, meta, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_data(data_resource, links, included_resources, meta)
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

    @classmethod
    def make_errors_response(cls, errors_resource, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_errors(errors_resource, kwargs.get("links", None))
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

