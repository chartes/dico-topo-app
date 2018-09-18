
from app import JSONAPIResponseFactory as RF, api_bp
from app.api.placename.facade import PlacenameFacade
from app.models import Placename


def get_placename(placename_id):
    e = Placename.query.filter(Placename.placename_id == placename_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "placename %s does not exist" % placename_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_placename_api_urls(app):
    app.api_url_registrar.register_get_routes(get_placename, Placename, PlacenameFacade)

    def register_placename_relationship_url(rel_name):
        return app.api_url_registrar.register_relationship_get_route(get_placename, PlacenameFacade, rel_name)

    register_placename_relationship_url('commune')
    register_placename_relationship_url('linked-commune')
    register_placename_relationship_url('linked-placenames')
    register_placename_relationship_url('old-labels')
    register_placename_relationship_url('alt-labels')
