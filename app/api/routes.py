import json
from flask import Response

from app import api_bp, db
from app.api.response_factory import JSONAPIResponseFactory  as RF
from tests.data.fixtures.entry import load_fixtures


@api_bp.route('/api/<api_version>/init')
def api_init(api_version):
    load_fixtures(db)
    return Response("init ok")


def register_get_route(obj_getter, facade, rel_name):
    """

    :param obj_getter:
    :param facade:
    :param rel_name:
    :param rel_links_fetcher:
    :param rel_resource_getter:
    :param rel_resource_identifier_fetcher:
    :return:
    """
    # ===============================
    # relationships self link route
    # ===============================
    rule = '/api/<api_version>/{type_plural}/<id>/relationships/{rel_name}'.format(
        type_plural=facade.TYPE_PLURAL, rel_name=rel_name
    )

    def resource_identifier_endpoint(api_version, id):
        entry, kwargs, errors = obj_getter(id)
        if entry is None:
            return RF.make_errors_response(errors, **kwargs)
        else:
            relationship = facade(entry).relationships[rel_name]
            data = {"links": relationship["links"], "data": relationship["resource_identifier"]}
            return RF.make_response(data, **kwargs)

    resource_identifier_endpoint.__name__ = "%s_%s_%s" % (facade.TYPE_PLURAL, rel_name.replace("-", "_"), resource_identifier_endpoint.__name__)
    # register the rule
    api_bp.add_url_rule(rule, endpoint=resource_identifier_endpoint.__name__, view_func=resource_identifier_endpoint)

    # ===================================
    # relationships related link route
    # ===================================
    rule = '/api/<api_version>/{type_plural}/<id>/{rel_name}'.format(
        type_plural=facade.TYPE_PLURAL, rel_name=rel_name
    )

    def resource_endpoint(api_version, id):
        entry, kwargs, errors = obj_getter(id)
        if entry is None:
            return RF.make_errors_response(errors, **kwargs)
        else:
            relationship = facade(entry).relationships[rel_name]
            return RF.make_data_response(relationship["resource"])

    resource_endpoint.__name__ = "%s_%s_%s" % (facade.TYPE_PLURAL, rel_name.replace("-", "_"), resource_endpoint.__name__)
    # register the rule
    api_bp.add_url_rule(rule, endpoint=resource_endpoint.__name__, view_func=resource_endpoint)


# =====================================
# import api routes
# =====================================
from app.api.entry import routes
from app.api.insee_commune import routes
from app.api.alt_orth import routes

