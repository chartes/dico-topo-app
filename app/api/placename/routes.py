from app.api.decorators import export_to
from app.api.placename.facade import PlacenameFacade
from app.models import Placename

from app.api.placename.decorators.exports.linkedplaces import export_placename_to_linkedplace, \
    export_placename_to_inline_linkedplace

export_funcs = {
    # the export format will be available under this http parameter value.
    # ex: http://localhost:5003/dico-topo/api/1.0/placenames?page[size]=200&without-relationships&export=linkedplaces
    #     or
    #     http://localhost:5003/dico-topo/api/1.0/placenames/DT02-02878?export=linkedplaces
    "linkedplaces": export_placename_to_linkedplace,
    "inlined-linkedplaces": export_placename_to_inline_linkedplace
}

def register_placename_api_urls(app):
    registrar = app.api_url_registrar

    registrar.register_get_routes(Placename, PlacenameFacade, decorators=[export_to(export_funcs)])

    registrar.register_relationship_get_route(PlacenameFacade, 'commune')
    registrar.register_relationship_get_route(PlacenameFacade, 'localization-commune')
    registrar.register_relationship_get_route(PlacenameFacade, 'linked-placenames')
    registrar.register_relationship_get_route(PlacenameFacade, 'old-labels')
    registrar.register_relationship_get_route(PlacenameFacade, 'alt-labels')
