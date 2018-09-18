from app import JSONAPIResponseFactory as RF, api_bp
from app.api.insee_commune.facade import CommuneFacade
from app.models import InseeCommune


def get_commune(insee_code):
    e = InseeCommune.query.filter(InseeCommune.insee_code == insee_code).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "commmune %s does not exist" % insee_code}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_insee_commune_api_urls(app):
    app.api_url_registrar.register_get_routes(get_commune, InseeCommune, CommuneFacade)

    def register_placename_relationship_url(rel_name):
        return app.api_url_registrar.register_relationship_get_route(get_commune, CommuneFacade, rel_name)

    register_placename_relationship_url('region')
    register_placename_relationship_url('departement')
    register_placename_relationship_url('arrondissement')
    register_placename_relationship_url('canton')
