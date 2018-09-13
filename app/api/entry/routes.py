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
        return RF.make_data_response(f_entry.commune_resource)


# ==============================
# Linked Commune relationship
# ==============================
@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/linked-commune')
def api_get_entry_relationships_linked_commune(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        data = {**f_entry.links_linked_commune, "data": f_entry.linked_commune_resource_identifier}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/linked-commune')
def api_get_entry_linked_commune(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        return RF.make_data_response(f_entry.linked_commune_resource)


# ==============================
# Linked Placenames relationship
# ==============================
@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/linked-placenames')
def api_get_entry_relationships_linked_placenames(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        data = {**f_entry.links_linked_placenames, "data": f_entry.linked_placenames_resource_identifiers}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/linked-placenames')
def api_get_entry_linked_placenames(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        return RF.make_data_response(f_entry.linked_placenames_resources)


# ==============================
# Alt Orths relationship
# ==============================
@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/alt-orths')
def api_get_entry_relationships_alt_orths(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        data = {**f_entry.links_alt_orths, "data": f_entry.alt_orths_resource_identifiers}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/alt-orths')
def api_get_entry_alt_orths(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        return RF.make_data_response(f_entry.alt_orths_resources)


# ==============================
# old Orths relationship
# ==============================
@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/old-orths')
def api_get_entry_relationships_old_orths(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        data = {**f_entry.links_old_orths, "data": f_entry.old_orths_resource_identifiers}
        return RF.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/old-orths')
def api_get_entry_old_orths(api_version, entry_id):
    entry, kwargs, errors = get_entry(entry_id)
    if entry is None:
        return RF.make_errors_response(errors, **kwargs)
    else:
        f_entry = EntryFacade(entry)
        return RF.make_data_response(f_entry.old_orths_resources)
