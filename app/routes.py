from flask import render_template, request

from app import app_bp


@app_bp.route("/")
def index():
    return render_template("main/index.html")


@app_bp.route('/placenames')
def get_placenames():
    num_start_page = request.args.get("filter[num_start_page]", 1)
    return render_template("main/placenames.html", num_start_page=num_start_page)

