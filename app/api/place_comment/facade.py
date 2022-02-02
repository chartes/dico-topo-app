import re

from app.api.citable_content.facade import CitableContentFacade
from app.api.place_description.facade import rewrite_link_target
from app.models import PlaceComment, Place


class PlaceCommentFacade(CitableContentFacade):
    """

    """
    TYPE = "place-comment"
    TYPE_PLURAL = "place-comments"

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
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
        # rewrite links in desc so they target to a better url
        if res['attributes']['content']:
            for (match, insee_code, label) in re.findall(r'(<a href="(\d+)">(.*?)</a>)', res['attributes']['content']):
                res['attributes']['content'] = re.sub(match, rewrite_link_target(insee_code, label), res['attributes']['content'])
            # remove unused links to feature types if any
            res['attributes']['content'] = re.sub(r'<a>(.*?)</a>', r'\1', res['attributes']['content'])
        return res


class FlatPlaceCommentFacade(PlaceCommentFacade):

    @property
    def resource(self):
        res = super(FlatPlaceCommentFacade, self).resource
        res['attributes']['place-id'] = self.obj.place_id

        # add a flattened resp statement to the comment facade
        from app.api.responsibility.facade import FlatResponsibilityFacade
        responsibility = FlatResponsibilityFacade("", self.obj.responsibility)

        res["attributes"]["responsibility"] = {
            "id": responsibility.id,
            **responsibility.resource["attributes"]
        }

        return res
