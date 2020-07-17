import re

from flask import current_app

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

    @property
    def resource(self):
        res = super(PlaceCommentFacade, self).resource
        co = self.obj.place.localization_commune

        # rewrite links in desc so they target to a better url
        if res['attributes']['content']:
            if co:
                rewritten = '<a href="{0}/places/{1}">'.format(current_app.config['APP_URL_PREFIX'], co.place.id)
                res['attributes']['content'] = re.sub(r'<a href="{0}">'.format(co.id), rewritten, res['attributes']['content'])

            # remove unused links to feature types if any
            res['attributes']['content'] = re.sub(r'<a>(.*?)</a>', r'\1', res['attributes']['content'])
        return res


class FlatPlaceCommentFacade(PlaceCommentFacade):

    @property
    def resource(self):
        res = super(FlatPlaceCommentFacade, self).resource

        # add a flattened resp statement to the comment facade
        from app.api.responsibility.facade import FlatResponsibilityFacade
        responsibility = FlatResponsibilityFacade("", self.obj.responsibility)

        res["attributes"]["responsibility"] = {
            "id": responsibility.id,
            **responsibility.resource["attributes"]
        }

        return res
