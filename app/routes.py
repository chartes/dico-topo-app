from flask import render_template, request, url_for

from app import app_bp


@app_bp.route("/")
def index():
    return render_template("main/index.html")


@app_bp.route('/placenames')
def get_placename_collection():
    num_start_page = request.args.get("filter[num_start_page]", 1)
    return render_template("main/placenames.html", num_start_page=num_start_page)


@app_bp.route('/placenames/<placename_id>')
def get_placename(placename_id):
    placename_url = url_for('api_bp.placenames_single_obj_endpoint', id=placename_id)
    return render_template("main/placename.html", placename_url=placename_url)

