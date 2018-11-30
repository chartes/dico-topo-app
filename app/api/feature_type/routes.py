from app import JSONAPIResponseFactory as RF, api_bp
from app.api.feature_type.facade import FeatureTypeFacade
from app.models import FeatureType


def register_feature_type_api_urls(app):
    app.api_url_registrar.register_get_routes(FeatureType, FeatureTypeFacade)
    app.api_url_registrar.register_relationship_get_route(FeatureTypeFacade, 'placename')




