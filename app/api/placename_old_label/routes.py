from app.api.placename_old_label.facade import PlacenameOldLabelFacade
from app.models import PlacenameOldLabel


def register_placename_old_label_api_urls(app):

    registrar = app.api_url_registrar

    registrar.register_get_routes(PlacenameOldLabel, PlacenameOldLabelFacade)

    registrar.register_relationship_get_route(PlacenameOldLabelFacade, 'placename')
    registrar.register_relationship_get_route(PlacenameOldLabelFacade, 'commune')
    registrar.register_relationship_get_route(PlacenameOldLabelFacade, 'localization-commune')

