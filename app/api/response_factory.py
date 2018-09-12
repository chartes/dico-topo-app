import json
from flask import Response


class JSONAPIResponseFactory:

    CONTENT_TYPE = "application/vnd.api+json; charset=utf-8"
    HEADERS = {"Access-Control-Allow-Origin": "*"}

    URL_PREFIX = ""

    @classmethod
    def set_url_prefix(cls, url_prefix):
        cls.URL_PREFIX = url_prefix

    @classmethod
    def prefix(cls, resource):
        print("TODO: PREFIX RESOURCES BY", cls.URL_PREFIX)
        return resource

    @classmethod
    def encapsulate(cls, toplevel, resource):
        return {
            toplevel: cls.prefix(resource),
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
    def make_response(cls, resource):
        return Response(
            json.dumps(resource, indent=2, ensure_ascii=False),
            content_type=JSONAPIResponseFactory.CONTENT_TYPE,
            headers=JSONAPIResponseFactory.HEADERS
        )

    @classmethod
    def make_data_response(cls, data_resource):
        resource = JSONAPIResponseFactory.encapsulate_data(data_resource)
        return JSONAPIResponseFactory.make_response(resource)

    @classmethod
    def make_errors_response(cls, errors_resource):
        resource = JSONAPIResponseFactory.encapsulate_errors(errors_resource)
        return JSONAPIResponseFactory.make_response(resource)

