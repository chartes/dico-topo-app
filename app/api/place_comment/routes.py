from app.api.place_comment.facade import PlaceCommentFacade
from app.models import PlaceComment


def register_place_comment_api_urls(app):
    app.api_url_registrar.register_get_routes(PlaceComment, PlaceCommentFacade)
    app.api_url_registrar.register_relationship_get_route(PlaceCommentFacade, 'responsibility')
