from app.api.responsibility.facade import ResponsibilityFacade
from app.api.user.facade import UserFacade
from app.models import User


def register_user_api_urls(app):
    app.api_url_registrar.register_get_routes(User, UserFacade)
    app.api_url_registrar.register_relationship_get_route(ResponsibilityFacade, 'responsibilities')
