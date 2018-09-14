from app import JSONAPIResponseFactory as RF, api_bp
from app.api.entry.facade import EntryFacade
from app.api.routes import register_get_route
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


def register_entry_relationship_url(rel_name):
    return register_get_route(get_entry, EntryFacade, rel_name)


register_entry_relationship_url('commune')
register_entry_relationship_url('linked-commune')
register_entry_relationship_url('linked-placenames')
register_entry_relationship_url('old-orths')
register_entry_relationship_url('alt-orths')
