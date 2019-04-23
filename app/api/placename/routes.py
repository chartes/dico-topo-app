from app.api.decorators import export_to
from app.api.placename.facade import PlacenameFacade
from app.models import Placename


def register_placename_api_urls(app):
    registrar = app.api_url_registrar

    registrar.register_get_routes(Placename, PlacenameFacade, decorators=[export_to('linkedplaces')])

    registrar.register_relationship_get_route(PlacenameFacade, 'commune')
    registrar.register_relationship_get_route(PlacenameFacade, 'localization-commune')
    registrar.register_relationship_get_route(PlacenameFacade, 'linked-placenames')
    registrar.register_relationship_get_route(PlacenameFacade, 'old-labels')
    registrar.register_relationship_get_route(PlacenameFacade, 'alt-labels')
