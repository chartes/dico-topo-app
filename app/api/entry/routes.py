from app import JSONAPIResponseFactory as RF, api_bp
from app.api.entry.facade import EntryFacade
from app.api.insee_commune.facade import CommuneFacade
from app.models import Entry


def get_entry(entry_id):
    e = Entry.query.filter(Entry.entry_id == entry_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "entry %s does not exist" % entry_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


@api_bp.route('/api/<api_version>/entries')
def api_get_all_entries(api_version):
    entries = Entry.query.all()
    return RF.make_data_response(
        [EntryFacade(entry).resource for entry in entries]
    )


@api_bp.route('/api/<api_version>/entries/<entry_id>')
def api_get_entry(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        return RF.make_data_response(f_entry.resource)


# ======================
# Commune relationship
# ======================
@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/commune')
def api_get_entry_relationships_commune(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        data = {**f_entry.links_commune, "data": f_entry.commune_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/commune')
def api_get_entry_commune(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        f_commune = CommuneFacade(f_entry.obj.commune)
        return RF.make_data_response(f_commune.resource)


