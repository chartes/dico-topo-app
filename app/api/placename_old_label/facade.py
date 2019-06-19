from flask import current_app

from app.api.abstract_facade import JSONAPIAbstractFacade


class PlacenameOldLabelFacade(JSONAPIAbstractFacade):
    """
    """
    TYPE = "placename-old-label"
    TYPE_PLURAL = "placename-old-labels"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import PlacenameOldLabel
        e = PlacenameOldLabel.query.filter(PlacenameOldLabel.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlacenameOldLabel %s does not exist" % id}]
        else:
            e = PlacenameOldLabelFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    def get_placename_resource_identifier(self):
        from app.api.placename.facade import PlacenameFacade
        return None if self.obj.placename is None else PlacenameFacade.make_resource_identifier(self.obj.placename.id,
                                                                                                PlacenameFacade.TYPE)

    def get_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade

        return None if (
                    self.obj.placename or self.obj.placename.commune is None) else CommuneFacade.make_resource_identifier(
            self.obj.placename.commune.id, CommuneFacade.TYPE)

    def get_localization_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade

        return None if (
                self.obj.placename is None or self.obj.placename.localization_commune is None
        ) else CommuneFacade.make_resource_identifier(self.obj.placename.localization_commune.id, CommuneFacade.TYPE)

    def get_placename_resource(self):
        from app.api.placename.facade import PlacenameFacade
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix, self.obj.placename,
                                                                       self.with_relationships_links,
                                                                       self.with_relationships_data).resource

    def get_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade

        return None if (self.obj.placename is None or self.obj.placename.commune is None) else CommuneFacade(
            self.url_prefix, self.obj.placename.commune,
            self.with_relationships_links,
            self.with_relationships_data
        ).resource

    def get_localization_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade

        return None if (
                self.obj.placename is None or self.obj.placename.localization_commune is None) else CommuneFacade(
            self.url_prefix, self.obj.placename.localization_commune,
            self.with_relationships_links,
            self.with_relationships_data
        ).resource

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
                "rich-label-node": self.obj.rich_label_node,
                "text-label-node": self.obj.text_label_node
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
        super(PlacenameOldLabelFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a PlacenameOldLabel
        """
        self.relationships = {
            "placename": {
                "links": self._get_links(rel_name="placename"),
                "resource_identifier_getter": self.get_placename_resource_identifier,
                "resource_getter": self.get_placename_resource
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
            }
        }

    @classmethod
    def get_index_name(cls):
        """
        index the old labels along the placenames
        :return:
        """
        from app.api.placename.facade import PlacenameFacade
        return "{prefix}__{env}__{index_name}".format(
            prefix=current_app.config.get("INDEX_PREFIX", ""),
            env=current_app.config.get("ENV"),
            index_name=PlacenameFacade.TYPE_PLURAL
        )

    def get_data_to_index_when_added(self, propagate):
        if self.obj.placename.commune:
            co = self.obj.placename.commune
        elif self.obj.placename.localization_commune:
            co = self.obj.placename.localization_commune
        else:
            co = None

        payload = {
            "id": self.obj.id,
            "placename-id": self.obj.placename.id,

            "type": self.TYPE,

            "label": self.obj.rich_label,
            "localization-insee-code": co.id if co else None,

            "dep-id": self.obj.placename.dpt,
            "reg-id": co.region.insee_code if co and co.region else None,
            "is-localized": co is not None,

            #"old-labels": [self.obj.rich_label],
        }
        return [{"id": self.obj.id, "index": self.get_index_name(), "payload": payload}]

    def get_data_to_index_when_removed(self, propagate):
        print("GOING TO BE REMOVED FROM INDEX:", [{"id": self.obj.id, "index": self.get_index_name()}])
        from app.api.placename.facade import PlacenameFacade
        return [
            {"id": self.obj.placename.id, "index": PlacenameFacade.get_index_name()},
            {"id": self.obj.id, "index": self.get_index_name()}
        ]


class PlacenameOldLabelSearchFacade(PlacenameOldLabelFacade):

    @property
    def resource(self):
        """ """
        if self.obj.placename.commune:
            co = self.obj.placename.commune
        elif self.obj.placename.localization_commune:
            co = self.obj.placename.localization_commune
        else:
            co = None

        res = {
            **self.resource_identifier,
            "attributes": {
                "placename-id": self.obj.placename.id,
                "placename-label": self.obj.placename.label,
                "placename-desc": self.obj.placename.desc,
                "localization-insee-code": co.id if co else None,
                "dpt": self.obj.placename.dpt,
                "region": co.region.label if co else None,
                "longlat": co.longlat if co else None,
                "rich-label": self.obj.rich_label,
                "text-label-node": self.obj.text_label_node,
                "rich-date": self.obj.rich_date,
                "rich-reference": self.obj.rich_reference,

                'geoname-id': co.geoname_id if co else None,
                'wikidata-item-id': co.wikidata_item_id if co else None,
                'wikipedia-url': co.wikipedia_url if co else None,
                'databnf-ark': co.databnf_ark if co else None,
                'viaf-id': co.viaf_id if co else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res

    def __init__(self, *args, **kwargs):
        super(PlacenameOldLabelSearchFacade, self).__init__(*args, **kwargs)
        self.relationships = {}


class PlacenameOldLabelMapFacade(PlacenameOldLabelSearchFacade):

    @property
    def resource(self):
        """ """

        if self.obj.placename.commune:
            co = self.obj.placename.commune
        elif self.obj.placename.localization_commune:
            co = self.obj.placename.localization_commune
        else:
            co = None

        res = {
            **self.resource_identifier,
            "attributes": {
                "placename-id": self.obj.placename.id,
                "longlat": self.obj.longlat,

                "dpt": "{0} - {1}".format(co.departement.insee_code, co.departement.label) if co else None,
                "region": "{0} - {1}".format(co.region.insee_code, co.region.label) if co else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res
