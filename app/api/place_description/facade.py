import re

from flask import current_app

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

    @property
    def resource(self):
        res = super(PlaceDescriptionFacade, self).resource
        co = self.obj.place.localization_commune

        # rewrite links in desc so they target to a better url
        if res['attributes']['content']:
            if co:
                rewritten = '<a href="{0}/places/{1}">'.format(current_app.config['APP_URL_PREFIX'], co.place.id)
                res['attributes']['content'] = re.sub(r'<a href="{0}">'.format(co.id), rewritten, res['attributes']['content'])

            # remove unused links to feature types if any
            res['attributes']['content'] = re.sub(r'<a>(.*?)</a>', r'\1', res['attributes']['content'])
        return res
