from app import JSONAPIResponseFactory as RF, api_bp
from app.api.insee_ref.facade import InseeRefFacade
from app.models import InseeRef


def get_insee_ref(insee_id):
    e = InseeRef.query.filter(InseeRef.id == insee_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "insee ref %s does not exist" % insee_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_insee_ref_api_urls(app):
    registrar = app.api_url_registrar
    registrar.register_get_routes(get_insee_ref, InseeRef, InseeRefFacade)
    registrar.register_relationship_get_route(get_insee_ref, InseeRefFacade, 'parent')
    registrar.register_relationship_get_route(get_insee_ref, InseeRefFacade, 'children')
