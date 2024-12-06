from dico_topo.app import JSONAPIResponseFactory as RF, api_bp
from dico_topo.app.api.bibl.facade import BiblFacade
from dico_topo.app.models import Bibl


def register_bibl_api_urls(app):
    app.api_url_registrar.register_get_routes(Bibl, BiblFacade)
    #app.api_url_registrar.register_relationship_get_route(BiblFacade, 'places')




