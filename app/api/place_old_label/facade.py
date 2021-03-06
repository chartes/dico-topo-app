import re

from flask import current_app

from app.api.abstract_facade import JSONAPIAbstractFacade


class PlaceOldLabelFacade(JSONAPIAbstractFacade):
    """
    """
    TYPE = "place-old-label"
    TYPE_PLURAL = "place-old-labels"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import PlaceOldLabel
        e = PlaceOldLabel.query.filter(PlaceOldLabel.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlaceOldLabel %s does not exist" % id}]
        else:
            e = PlaceOldLabelFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    def get_place_resource_identifier(self, rel_facade=None):
        from app.api.place.facade import PlaceFacade
        rel_facade = PlaceFacade if not rel_facade else rel_facade

        return None if self.obj.place is None else rel_facade.make_resource_identifier(self.obj.place.id,
                                                                                       rel_facade.TYPE)

    def get_commune_resource_identifier(self, rel_facade=None):
        from app.api.insee_commune.facade import CommuneFacade
        rel_facade = CommuneFacade if not rel_facade else rel_facade

        return None if (
                    self.obj.place or self.obj.place.commune is None) else rel_facade.make_resource_identifier(
            self.obj.place.commune.id, rel_facade.TYPE)

    def get_localization_commune_resource_identifier(self, rel_facade=None):
        from app.api.insee_commune.facade import CommuneFacade
        rel_facade = CommuneFacade if not rel_facade else rel_facade

        return None if (
                self.obj.place is None or self.obj.place.localization_commune is None
        ) else rel_facade.make_resource_identifier(self.obj.place.localization_commune.id, rel_facade.TYPE)

    def get_place_resource(self, rel_facade=None):
        from app.api.place.facade import PlaceFacade
        rel_facade = PlaceFacade if not rel_facade else rel_facade

        return None if self.obj.place is None else rel_facade(self.url_prefix, self.obj.place,
                                                                       self.with_relationships_links,
                                                                       self.with_relationships_data).resource

    def get_commune_resource(self, rel_facade=None):
        from app.api.insee_commune.facade import CommuneFacade
        rel_facade = CommuneFacade if not rel_facade else rel_facade

        return None if (self.obj.place is None or self.obj.place.commune is None) else rel_facade(
            self.url_prefix, self.obj.place.commune,
            self.with_relationships_links,
            self.with_relationships_data
        ).resource

    def get_localization_commune_resource(self, rel_facade=None):
        from app.api.insee_commune.facade import CommuneFacade
        rel_facade = CommuneFacade if not rel_facade else rel_facade

        return None if (
                self.obj.place is None or self.obj.place.localization_commune is None) else rel_facade(
            self.url_prefix, self.obj.place.localization_commune,
            self.with_relationships_links,
            self.with_relationships_data
        ).resource

    @staticmethod
    def parse_date(d):
        # try parsing the date field and put NULL if impossible
        try:
            parsed_text_date = int(d)
        except Exception as e:
            #print(e)
            parsed_text_date = None
        return parsed_text_date

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                "rich-label": self.obj.rich_label,
                "rich-date": self.obj.rich_date,
                "text-date": self.obj.text_date,
                "rich-reference": self.obj.rich_reference,
            },
            "meta": self.meta,
            "links": {
                "self": self.self_link
            }
        }
        if self.with_relationships_links:
            res["relationships"] = self.get_exposed_relationships()

        return res

    def __init__(self, *args, **kwargs):
        super(PlaceOldLabelFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a PlaceOldLabel
        """
        from app.api.responsibility.facade import ResponsibilityFacade
        self.relationships = {
            "place": {
                "links": self._get_links(rel_name="place"),
                "resource_identifier_getter": self.get_place_resource_identifier,
                "resource_getter": self.get_place_resource
            },
            "commune": {
                "links": self._get_links(rel_name="commune"),
                "resource_identifier_getter": self.get_commune_resource_identifier,
                "resource_getter": self.get_commune_resource
            },
            "localization-commune": {
                "links": self._get_links(rel_name="localization-commune"),
                "resource_identifier_getter": self.get_localization_commune_resource_identifier,
                "resource_getter": self.get_localization_commune_resource
            },
            "responsibility": {
                "links": self._get_links(rel_name="responsibility"),
                "resource_identifier_getter": self.get_related_resource_identifiers(ResponsibilityFacade,  "responsibility", False),
                "resource_getter": self.get_related_resources(ResponsibilityFacade, "responsibility", False),
            }
        }

    @classmethod
    def get_index_name(cls):
        """
        index the old labels along the places
        :return:
        """
        from app.api.place.facade import PlaceFacade
        return "{prefix}__{env}__{index_name}".format(
            prefix=current_app.config.get("INDEX_PREFIX", ""),
            env=current_app.config.get("ENV"),
            index_name=PlaceFacade.TYPE_PLURAL
        )

    def get_data_to_index_when_added(self, propagate):
        co = self.obj.place.related_commune

        label = re.sub(r'<dfn>(.*?)</dfn>', r'\1', self.obj.rich_label)
        payload = {
            "id": self.obj.id,
            "place-id": self.obj.place.id,
            "place-label": self.obj.place.label,

            "type": self.TYPE,
            "label": label,

            "localization-insee-code": co.id if co else None,
            "commune-label": co.NCCENR if co else None,

            "dep-id": self.obj.place.dpt,
            "ctn-id": co.canton.id if co and co.canton else None,
            "reg-id": co.region.insee_code if co and co.region else None,

            "ctn-label": co.canton.label if co and co.canton else None,

            "is-localized": co is not None,

            "text-date": self.parse_date(self.obj.text_date),
        }

        return [{"id": self.obj.id, "index": self.get_index_name(), "payload": payload}]

    def get_data_to_index_when_removed(self, propagate):
        print("GOING TO BE REMOVED FROM INDEX:", [{"id": self.obj.id, "index": self.get_index_name()}])
        from app.api.place.facade import PlaceFacade
        return [
            {"id": self.obj.place.id, "index": PlaceFacade.get_index_name()},
            {"id": self.obj.id, "index": self.get_index_name()}
        ]


class PlaceOldLabelSearchFacade(PlaceOldLabelFacade):

    @property
    def resource(self):
        """ """
        from app.api.place_description.facade import PlaceDescriptionFacade

        co = self.obj.place.related_commune

        res = {
            **self.resource_identifier,
            "attributes": {
                "place-id": self.obj.place.id,
                "place-label": self.obj.place.label,
                "place-desc": [d.resource["attributes"]["content"] for d in [PlaceDescriptionFacade("", e)
                               for e in self.obj.place.descriptions]],
                "localization-insee-code": co.id if co else None,
                "commune-label": co.NCCENR if co else None,
                "dpt": self.obj.place.dpt,
                "canton": co.canton.label if co and co.canton else None,
                "region": co.region.label if co and co.region else None,
                "longlat": co.longlat if co else None,
                "rich-label": self.obj.rich_label,
                "text-date": self.parse_date(self.obj.text_date),
                "rich-date": self.obj.rich_date,
                "rich-reference": self.obj.rich_reference,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res

    def __init__(self, *args, **kwargs):
        super(PlaceOldLabelSearchFacade, self).__init__(*args, **kwargs)
        self.relationships = {}


class PlaceOldLabelMapFacade(PlaceOldLabelSearchFacade):

    @property
    def resource(self):
        """ """
        co = self.obj.place.related_commune

        res = {
            **self.resource_identifier,
            "attributes": {
                "place-id": self.obj.place.id,
                "place-label": self.obj.place.label,
                "longlat": self.obj.longlat,

                "dpt": "{0} - {1}".format(co.departement.insee_code, co.departement.label) if co and co.departement else None,
                "region": "{0} - {1}".format(co.region.insee_code, co.region.label) if co and co.region else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res


class FlatPlaceOldLabelFacade(PlaceOldLabelFacade):

    @property
    def resource(self):
        res = super(FlatPlaceOldLabelFacade, self).resource

        # add a flattened resp statement to the old label facade
        from app.api.responsibility.facade import FlatResponsibilityFacade
        responsibility = FlatResponsibilityFacade("", self.obj.responsibility)

        res["attributes"]["responsibility"] = {
            "id": responsibility.id,
            **responsibility.resource["attributes"]
        }

        return res
