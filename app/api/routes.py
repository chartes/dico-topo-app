import json
from flask import Response

from app import api_bp


@api_bp.route('/api/<api_version>/init')
def api_init(api_version):
    # load_fixtures(db)
    return Response("init ok")



