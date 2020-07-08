from app.api.citable_content.facade import CitableContentFacade
from app.models import PlaceDescription


class PlaceDescriptionFacade(CitableContentFacade):
    """

    """
    TYPE = "place-description"
    TYPE_PLURAL = "place-descriptions"

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):

        e = PlaceDescription.query.filter(PlaceDescription.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlaceDescription %s does not exist" % id}]
        else:
            e = PlaceDescriptionFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors
