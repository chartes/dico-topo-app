from app.api.responsibility.facade import ResponsibilityFacade
from app.models import Responsibility


def register_responsibility_api_urls(app):
    app.api_url_registrar.register_get_routes(Responsibility, ResponsibilityFacade)
    app.api_url_registrar.register_relationship_get_route(ResponsibilityFacade, 'bibl')
    app.api_url_registrar.register_relationship_get_route(ResponsibilityFacade, 'user')
