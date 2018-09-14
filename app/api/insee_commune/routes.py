from app import JSONAPIResponseFactory as RF, api_bp
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade
from app.api.routes import register_get_route
from app.models import InseeCommune


def get_commune(insee_id):
    e = InseeCommune.query.filter(InseeCommune.insee_id == insee_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "commmune %s does not exist" % insee_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


@api_bp.route('/api/<api_version>/communes')
def api_get_all_communes(api_version):
    communes = InseeCommune.query.all()
    return RF.make_data_response(
        [CommuneFacade(e).resource for e in communes]
    )


@api_bp.route('/api/<api_version>/communes/<insee_id>')
def api_get_commune(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        return RF.make_data_response(CommuneFacade(commune).resource)


def register_commune_relationship_url(rel_name):
    register_get_route(get_commune, CommuneFacade, rel_name)


register_commune_relationship_url('region')
register_commune_relationship_url('departement')
register_commune_relationship_url('arrondissement')
register_commune_relationship_url('canton')

