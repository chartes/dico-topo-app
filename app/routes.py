from flask import render_template, request, url_for, current_app, make_response
from flask_jwt_extended import unset_jwt_cookies, set_access_cookies, create_access_token
from flask_login import current_user

from app import app_bp, api_bp


#@app_bp.route("/")
#def index():
#    resp = make_response(render_template("main/index.html"))
#
#    user = current_user
#    if not user.is_anonymous:
#        access_token = create_access_token(identity=user.to_json())
#        resp.headers["login"] = True
#        set_access_cookies(resp, access_token)
#    else:
#        resp.headers["logout"] = True
#        unset_jwt_cookies(resp)
#
#    return resp, 200
#
#
#@app_bp.route("/documentation")
#def documentation():
#    return render_template("docs/docs.html")
#
#
#@app_bp.route('/placenames')
#def get_placename_collection():
#    num_start_page = request.args.get("filter[num_start_page]", 1)
#    return render_template("main/placenames.html", num_start_page=num_start_page)
#
#
#@app_bp.route('/placenames/<placename_id>')
#def get_placename(placename_id):
#    placename_url = url_for('api_bp.placenames_single_obj_endpoint', id=placename_id)
#    return render_template("main/placename.html", placename_url=placename_url)


