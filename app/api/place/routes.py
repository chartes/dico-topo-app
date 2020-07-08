from app.api.decorators import export_to
from app.api.place.facade import PlaceFacade
from app.models import Place

from app.api.place.decorators.exports.linkedplaces import export_place_to_linkedplace, \
    export_place_to_inline_linkedplace

export_funcs = {
    # the export format will be available under this http parameter value.
    # ex: http://localhost:5003/dico-topo/api/1.0/places?page[size]=200&without-relationships&export=linkedplaces
    #     or
    #     http://localhost:5003/dico-topo/api/1.0/places/DT02-02878?export=linkedplaces
    "linkedplaces": export_place_to_linkedplace,
    "inlined-linkedplaces": export_place_to_inline_linkedplace
}

def register_place_api_urls(app):
    registrar = app.api_url_registrar

    registrar.register_get_routes(Place, PlaceFacade, decorators=[export_to(export_funcs)])

    registrar.register_relationship_get_route(PlaceFacade, 'commune')
    registrar.register_relationship_get_route(PlaceFacade, 'localization-commune')
    registrar.register_relationship_get_route(PlaceFacade, 'linked-places')
    registrar.register_relationship_get_route(PlaceFacade, 'old-labels')
    registrar.register_relationship_get_route(PlaceFacade, 'alt-labels')
    registrar.register_relationship_get_route(PlaceFacade, 'responsibility')
    registrar.register_relationship_get_route(PlaceFacade, 'descriptions')
    registrar.register_relationship_get_route(PlaceFacade, 'comments')
    registrar.register_relationship_get_route(PlaceFacade, 'place-feature-types')
