import json
from flask import Response

from app import api_bp, db
from app.api.response_factory import JSONAPIResponseFactory
from app.models import Entry, InseeRef, InseeCommune, AltOrth, OldOrth
from tests.data.fixtures.entry import load_fixtures


@api_bp.route('/api/<api_version>/init')
def api_init(api_version):
    load_fixtures(db)
    return Response("init ok")


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


@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/insee-commune')
def api_get_entry_relationships_insee_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        data = {
            **e.links_insee_commune,
            "data": e.insee.resource_identifier
        }
        return JSONAPIResponseFactory.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/insee-commune')
def api_get_entry_insee_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        return JSONAPIResponseFactory.make_data_response(e.insee.resource)

