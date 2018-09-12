import json
from flask import Response


class JSONAPIResponseFactory:

    CONTENT_TYPE = "application/vnd.api+json; charset=utf-8"
    HEADERS = {"Access-Control-Allow-Origin": "*",
               "Access-Control-Allow-Methods": ["GET", "POST", "DELETE", "PATCH"]}

    @classmethod
    def encapsulate(cls, toplevel, resource):
        return {
            toplevel: resource,
            "meta": {

            },
            "jsonapi": {
                "version": "1.0"
            }
        }

    @classmethod
    def encapsulate_data(cls, resource):
        return JSONAPIResponseFactory.encapsulate("data", resource)

    @classmethod
    def encapsulate_errors(cls, resource):
        return JSONAPIResponseFactory.encapsulate("errors", resource)

    @classmethod
    def make_response(cls, resource, **kwargs):
        return Response(
            json.dumps(resource, indent=2, ensure_ascii=False),
            content_type=JSONAPIResponseFactory.CONTENT_TYPE,
            headers=JSONAPIResponseFactory.HEADERS,
            **kwargs
        )

    @classmethod
    def make_data_response(cls, data_resource, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_data(data_resource)
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

    @classmethod
    def make_errors_response(cls, errors_resource, **kwargs):
        resource = JSONAPIResponseFactory.encapsulate_errors(errors_resource)
        return JSONAPIResponseFactory.make_response(resource, **kwargs)

