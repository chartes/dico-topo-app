from app import JSONAPIResponseFactory as RF, api_bp
from app.api.alt_orth.facade import AltOrthFacade
from app.api.routes import register_get_route
from app.models import AltOrth


def get_alt_orth(entry_id):
    e = AltOrth.query.filter(AltOrth.entry_id == entry_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "alternative orthography %s does not exist" % entry_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


@api_bp.route('/api/<api_version>/alt-orths')
def api_get_all_alt_orths(api_version):
    alt_orths = AltOrth.query.all()
    return RF.make_data_response(
        [AltOrthFacade(alt_orth).resource for alt_orth in alt_orths]
    )


@api_bp.route('/api/<api_version>/alt-orths/<entry_id>')
def api_get_alt_orth(api_version, entry_id):
    alt_orth, kwargs, errors = get_alt_orth(entry_id)
    if alt_orth is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_alt_orth = AltOrthFacade(alt_orth)
        return RF.make_data_response(f_alt_orth.resource)


def register_alt_orth_relationship_url(rel_name):
    return register_get_route(get_alt_orth, AltOrthFacade, rel_name)


register_alt_orth_relationship_url('entry')