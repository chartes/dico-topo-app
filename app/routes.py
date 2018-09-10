from flask import render_template

from app import app_bp


@app_bp.route("/")
def index():
    return render_template("main/index.html")