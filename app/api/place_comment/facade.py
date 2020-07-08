from app.api.citable_content.facade import CitableContentFacade
from app.models import PlaceComment


class PlaceCommentFacade(CitableContentFacade):
    """

    """
    TYPE = "place-comment"
    TYPE_PLURAL = "place-comments"

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import User

        e = PlaceComment.query.filter(PlaceComment.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlaceComment %s does not exist" % id}]
        else:
            e = PlaceCommentFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors
