from app.api.place_alt_label.facade import PlaceAltLabelFacade
from app.models import PlaceAltLabel


def register_place_alt_label_api_urls(app):

    registrar = app.api_url_registrar

    registrar.register_get_routes(PlaceAltLabel, PlaceAltLabelFacade)

    registrar.register_relationship_get_route(PlaceAltLabelFacade, 'place')
