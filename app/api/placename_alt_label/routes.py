from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
from app.models import PlacenameAltLabel


def register_placename_alt_label_api_urls(app):

    registrar = app.api_url_registrar

    registrar.register_get_routes(PlacenameAltLabel, PlacenameAltLabelFacade)

    registrar.register_relationship_get_route(PlacenameAltLabelFacade, 'placename')
