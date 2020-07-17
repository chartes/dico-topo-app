import re

from flask import current_app

from app.api.citable_content.facade import CitableContentFacade
from app.models import PlaceDescription, InseeCommune


def rewrite_link_target(insee_code):
    co = InseeCommune.query.filter(InseeCommune.id == insee_code).first()
    if co:
        return '<a href="{0}/places/{1}">'.format(current_app.config['APP_URL_PREFIX'], co.place.id)
    else:
        return '<a>'


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

    @property
    def resource(self):
        res = super(PlaceDescriptionFacade, self).resource

        # rewrite links in desc so they target to a better url
        if res['attributes']['content']:
            for (match, insee_code) in re.findall(r'(<a href="(\d+)">)', res['attributes']['content']):
                res['attributes']['content'] = re.sub(match, rewrite_link_target(insee_code), res['attributes']['content'])

            # remove unused links to feature types if any
            res['attributes']['content'] = re.sub(r'<a>(.*?)</a>', r'\1', res['attributes']['content'])
        return res


class FlatPlaceDescriptionFacade(PlaceDescriptionFacade):

    @property
    def resource(self):
        res = super(FlatPlaceDescriptionFacade, self).resource

        # add a flattened resp statement to the description facade

        from app.api.responsibility.facade import FlatResponsibilityFacade
        responsibility = FlatResponsibilityFacade("", self.obj.responsibility)

        res["attributes"]["responsibility"] = {
            "id": responsibility.id,
            **responsibility.resource["attributes"]
        }

        return res
