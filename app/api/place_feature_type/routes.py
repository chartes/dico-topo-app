from app import JSONAPIResponseFactory as RF, api_bp
from app.api.place_feature_type.facade import PlaceFeatureTypeFacade
from app.models import PlaceFeatureType


def register_feature_type_api_urls(app):
    app.api_url_registrar.register_get_routes(PlaceFeatureType, PlaceFeatureTypeFacade)
    app.api_url_registrar.register_relationship_get_route(PlaceFeatureTypeFacade, 'place')




