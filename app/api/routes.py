from flask import Response, request

from app import api_bp
from app.api.capabilities import api_get_capabilities


@api_bp.route('/api/<api_version>/init')
def api_init(api_version):
    # load_fixtures(db)
    return Response("init ok")


@api_bp.route("/api/<api_version>/search/<index>")
def api_search(api_version, index="_all"):
    pass


