from app import JSONAPIResponseFactory as RF, api_bp
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade
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


# ==========================
# Region relationship
# ==========================
@api_bp.route('/api/<api_version>/communes/<insee_id>/relationships/region')
def api_get_commune_relationships_region(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        data = {**f_commune.links_dep, "data": f_commune.departement_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/communes/<insee_id>/region')
def api_get_commune_region(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        return RF.make_data_response(f_commune.region_resource)


# ==========================
# Departement relationship
# ==========================
@api_bp.route('/api/<api_version>/communes/<insee_id>/relationships/departement')
def api_get_commune_relationships_departement(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        data = {**f_commune.links_dep, "data": f_commune.departement_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/communes/<insee_id>/departement')
def api_get_commune_departement(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        return RF.make_data_response(f_commune.departement_resource)


# =============================
# Arrondissement relationship
# ============================
@api_bp.route('/api/<api_version>/communes/<insee_id>/relationships/arrondissement')
def api_get_commune_relationships_arrondissement(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        data = {**f_commune.links_dep, "data": f_commune.departement_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/communes/<insee_id>/arrondissement')
def api_get_commune_arrondissement(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        return RF.make_data_response(f_commune.arrondissement_resource)


# =============================
# Canton relationship
# ============================
@api_bp.route('/api/<api_version>/communes/<insee_id>/relationships/canton')
def api_get_commune_relationships_canton(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        data = {**f_commune.links_dep, "data": f_commune.departement_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/communes/<insee_id>/canton')
def api_get_commune_canton(api_version, insee_id):
    commune, kwargs, errors = get_commune(insee_id)
    if commune is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_commune = CommuneFacade(commune)
        return RF.make_data_response(f_commune.canton_resource)

