from app.api.place_description.facade import PlaceDescriptionFacade
from app.models import PlaceDescription


def register_place_description_api_urls(app):
    app.api_url_registrar.register_get_routes(PlaceDescription, PlaceDescriptionFacade)
    app.api_url_registrar.register_relationship_get_route(PlaceDescriptionFacade, 'responsibility')
