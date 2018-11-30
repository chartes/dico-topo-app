from app.api.insee_ref.facade import InseeRefFacade
from app.models import InseeRef



def register_insee_ref_api_urls(app):
    registrar = app.api_url_registrar

    registrar.register_get_routes(InseeRef, InseeRefFacade)

    registrar.register_relationship_get_route(InseeRefFacade, 'parent')
    registrar.register_relationship_get_route(InseeRefFacade, 'children')
