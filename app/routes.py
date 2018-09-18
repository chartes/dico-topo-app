import json
from flask import render_template, current_app

from app import app_bp
from app.api.placename.facade import PlacenameFacade
from app.models import Placename


@app_bp.route("/")
def index():
    return render_template("main/index.html")


@app_bp.route('/placenames')
def get_placenames():
    objs = Placename.query.all()#order_by(Placename.placename_id.desc()).paginate(1, 100, error_out=False).items

    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()
    placenames = [PlacenameFacade(current_app.config["API_URL_PREFIX"], obj).resource for obj in objs]
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

    return render_template("main/placenames.html", placenames=placenames)

