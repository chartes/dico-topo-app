from app import JSONAPIResponseFactory, api_bp
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


@api_bp.route('/api/<api_version>/entries/<entry_id>')
def api_get_entry(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        return JSONAPIResponseFactory.make_data_response(e.resource)


@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/commune')
def api_get_entry_relationships_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        data = {
            **e.links_commune,
            "data": None if e.commune is None else e.commune.resource_identifier
        }
        return JSONAPIResponseFactory.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/commune')
def api_get_entry_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        return JSONAPIResponseFactory.make_data_response(e.commune.resource)


@api_bp.route('/api/<api_version>/entries')
def api_get_all_entries(api_version):
    entries = Entry.query.all()
    return JSONAPIResponseFactory.make_data_response([e.resource for e in entries])
