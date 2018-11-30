from flask import render_template, request, url_for, current_app

from app import app_bp, api_bp


@app_bp.route("/")
def index():
    return render_template("main/index.html")


@app_bp.route("/documentation")
def documentation():
    return render_template("docs/docs.html")


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
    from app import JSONAPIResponseFactory

    res, total = current_app.api_url_registrar.search(index="placename,placename_old_label", expression=term, fields=["label", "rich_label_node"])
    print(len(res["placename_old_label"]))
    return JSONAPIResponseFactory.make_data_response(
        { **dict([(idx, [o.id for o in r]) for idx, r in res.items()])}, links=[], included_resources=[], meta={"total-if-it-was-not-capped-to-10000": total}
    )
