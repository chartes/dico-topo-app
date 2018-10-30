from app.api.placename_old_label.facade import PlacenameOldLabelFacade
from app.models import PlacenameOldLabel


def get_placename_old_label(id):
    e = PlacenameOldLabel.query.filter(PlacenameOldLabel.id == int(id)).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "placename old label '%s' does not exist" % id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


def register_placename_old_label_api_urls(app):
    app.api_url_registrar.register_get_routes(get_placename_old_label, PlacenameOldLabel, PlacenameOldLabelFacade)
    app.api_url_registrar.register_relationship_get_route(get_placename_old_label, PlacenameOldLabelFacade, 'placename')
    app.api_url_registrar.register_relationship_get_route(get_placename_old_label, PlacenameOldLabelFacade, 'old-labels')
