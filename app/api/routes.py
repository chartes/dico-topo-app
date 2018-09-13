import json
from flask import Response

from app import api_bp, db
from app.api.response_factory import JSONAPIResponseFactory  as RF
from tests.data.fixtures.entry import load_fixtures



@api_bp.route('/api/<api_version>/init')
def api_init(api_version):
    load_fixtures(db)
    return Response("init ok")


def make_get_route(obj_getter, facade, rel_name, rel_links_fetcher, rel_resource_getter, rel_resource_identifier_fetcher):
    rule = '/api/<api_version>/{type_plural}/<id>/relationships/{rel_name}'.format(
        type_plural=facade.TYPE_PLURAL, rel_name=rel_name
    )

    def resource_identifier_endpoint(api_version, id):
        entry, kwargs, errors = obj_getter(id)
        if entry is None:
            return RF.make_errors_response(errors, **kwargs)
        else:
            f = facade(entry)
            data = {**(rel_links_fetcher(f)), "data": rel_resource_identifier_fetcher(f)}
            return RF.make_response(data, **kwargs)

    resource_identifier_endpoint.__name__ = "%s_%s_%s" % (facade.TYPE_PLURAL, rel_name, resource_identifier_endpoint.__name__)
    api_bp.add_url_rule(rule, endpoint=resource_identifier_endpoint.__name__, view_func=resource_identifier_endpoint)

    rule = '/api/<api_version>/{type_plural}/<id>/{rel_name}'.format(
        type_plural=facade.TYPE_PLURAL, rel_name=rel_name
    )

    def resource_endpoint(api_version, id):
        entry, kwargs, errors = obj_getter(id)
        if entry is None:
            return RF.make_errors_response(errors, **kwargs)
        else:
            f = facade(entry)
            return RF.make_data_response(rel_resource_getter(f))

    resource_endpoint.__name__ = "%s_%s_%s" % (facade.TYPE_PLURAL, rel_name, resource_endpoint.__name__)
    api_bp.add_url_rule(rule, endpoint=resource_endpoint.__name__, view_func=resource_endpoint)


from app.api.entry import routes
from app.api.insee_commune import routes
