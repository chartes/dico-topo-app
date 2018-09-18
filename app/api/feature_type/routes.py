from app import JSONAPIResponseFactory as RF, api_bp
from app.api.feature_type.facade import FeatureTypeFacade
from app.models import FeatureType


def get_feature_type(id):
    e = FeatureType.query.filter(FeatureType.id == id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "feature type %s does not exist" % id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_feature_type_api_urls(app):
    app.api_url_registrar.register_get_routes(get_feature_type, FeatureType, FeatureTypeFacade)
    app.api_url_registrar.register_relationship_get_route(get_feature_type, FeatureTypeFacade, 'placename')




