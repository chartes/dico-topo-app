import re

from Levenshtein._levenshtein import distance
from flask import current_app

from app.api.citable_content.facade import CitableContentFacade
from app.models import PlaceDescription, Place


def rewrite_link_target(insee_code, place_label):
    places = Place.query.filter(Place.commune_insee_code == insee_code).all()
    length = len(places)
    place = None

    if length == 1:
        place = places[0]
    elif length > 1:
        # find exact match
        for p in places:
            if p.label == place_label:
                place = p
                break
        if place is None:
            # find best match
            distances = [distance(place_label, p.label) for p in places]
            best_match_idx = distances.index(min(distances))
            place = places[best_match_idx]

    if place:
        return '<a href="{0}/places/{1}">{2}</a>'.format(current_app.config['APP_URL_PREFIX'], place.id, place_label)
    else:
        print('@@ NOT FOUND', insee_code, place_label)
        return place_label


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
            for (match, insee_code, label) in re.findall(r'(<a href="(\d+)">(.*?)</a>)', res['attributes']['content']):
                res['attributes']['content'] = re.sub(match, rewrite_link_target(insee_code, label), res['attributes']['content'])
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
