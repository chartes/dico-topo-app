from app.api.place_old_label.facade import PlaceOldLabelFacade
from app.models import PlaceOldLabel


def register_place_old_label_api_urls(app):

    registrar = app.api_url_registrar

    registrar.register_get_routes(PlaceOldLabel, PlaceOldLabelFacade)

    registrar.register_relationship_get_route(PlaceOldLabelFacade, 'place')
    registrar.register_relationship_get_route(PlaceOldLabelFacade, 'commune')
    registrar.register_relationship_get_route(PlaceOldLabelFacade, 'localization-commune')

