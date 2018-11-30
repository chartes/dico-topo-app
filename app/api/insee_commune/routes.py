from app.api.insee_commune.facade import CommuneFacade
from app.models import InseeCommune


def register_insee_commune_api_urls(app):
    registrar = app.api_url_registrar

    registrar.register_get_routes(InseeCommune, CommuneFacade)

    registrar.register_relationship_get_route(CommuneFacade, 'placename')
    registrar.register_relationship_get_route(CommuneFacade, 'localized-placenames')
    registrar.register_relationship_get_route(CommuneFacade, 'region')
    registrar.register_relationship_get_route(CommuneFacade, 'departement')
    registrar.register_relationship_get_route(CommuneFacade, 'arrondissement')
    registrar.register_relationship_get_route(CommuneFacade, 'canton')
