from app import JSONAPIResponseFactory as RF, api_bp
from app.api.entry.facade import EntryFacade
from app.api.routes import make_get_route
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


def make_get_entry_route(*args, **kwargs):
    make_get_route(get_entry, *args, **kwargs)


# ======================
# Commune relationship
# ======================
make_get_entry_route(EntryFacade, 'commune',
                     lambda f: f.links_commune,
                     lambda f: f.commune_resource,
                     lambda f: f.commune_resource_identifier)
# ==============================
# Linked Commune relationship
# ==============================
make_get_entry_route(EntryFacade, 'linked-commune',
                     lambda f: f.links_linked_commune,
                     lambda f: f.linked_commune_resource,
                     lambda f: f.linked_commune_resource_identifier)
# ==============================
# Linked Placenames relationship
# ==============================
make_get_entry_route(EntryFacade, 'linked-placenames',
                     lambda f: f.links_linked_placenames,
                     lambda f: f.linked_placenames_resources,
                     lambda f: f.linked_placenames_resource_identifiers)
# ==============================
# old Orths relationship
# ==============================
make_get_entry_route(EntryFacade, 'old-orths',
                     lambda f: f.links_old_orths,
                     lambda f: f.old_orths_resources,
                     lambda f: f.old_orths_resource_identifiers)
# ==============================
# Alt Orths relationship
# ==============================
make_get_entry_route(EntryFacade, 'alt-orths',
                     lambda f: f.links_alt_orths,
                     lambda f: f.alt_orths_resources,
                     lambda f: f.alt_orths_resource_identifiers)
