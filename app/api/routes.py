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




from app.api.entry import routes
