from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
from app.models import PlacenameAltLabel


def get_placename_alt_label(id):
    e = PlacenameAltLabel.query.filter(PlacenameAltLabel.id == id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "placename alternative label '%s' does not exist" % id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_placename_alt_label_api_urls(app):
    app.api_url_registrar.register_get_routes(get_placename_alt_label, PlacenameAltLabel, PlacenameAltLabelFacade)
    app.api_url_registrar.register_relationship_get_route(get_placename_alt_label, PlacenameAltLabelFacade, 'placename')
