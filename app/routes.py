from flask import render_template, request, url_for

from app import app_bp, api_bp


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


@api_bp.route('/api/1.0/dev/search/<term>')
def dev_search_without_facade(term):
    from app.models import Placename
    from app import JSONAPIResponseFactory

    p = Placename.query.filter(Placename.label.ilike(term)).all()

    return JSONAPIResponseFactory.make_data_response(
                        [(pl.label, pl.desc) for pl in p], links=[], included_resources=[], meta={"total-count": len(p)}
                    )


@api_bp.route('/api/1.0/dev/search-without-rel-data/<term>')
def dev_search_with_facade_without_rel_data(term):
    from app.models import Placename
    from app.api.placename.facade import PlacenameFacade
    from app import JSONAPIResponseFactory

    placenames = Placename.query.filter(Placename.label.ilike(term)).all()
    data = [obj.resource for obj in [PlacenameFacade("url/prefix", p, with_relationships_data=False) for p in placenames]]

    return JSONAPIResponseFactory.make_data_response(
                        data, links=[], included_resources=[], meta={"total-count": len(data)}
    )


@api_bp.route('/api/1.0/dev/search-without-rel/<term>')
def dev_search_with_facade_without_rel(term):
    from app.models import Placename
    from app.api.placename.facade import PlacenameFacade
    from app import JSONAPIResponseFactory

    placenames = Placename.query.filter(Placename.label.ilike(term)).all()
    data = [obj.resource for obj in [PlacenameFacade("url/prefix", p,
                                                     with_relationships_links=False,
                                                     with_relationships_data=False)
                                     for p in placenames]]

    return JSONAPIResponseFactory.make_data_response(
        data, links=[], included_resources=[], meta={"total-count": len(data)}
    )