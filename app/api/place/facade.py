
from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.place_feature_type.facade import PlaceFeatureTypeFacade


class PlaceFacade(JSONAPIAbstractFacade):
    """
    """
    TYPE = "place"
    TYPE_PLURAL = "places"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import Place

        e = Place.query.filter(Place.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "Place %s does not exist" % id}]
        else:
            e = PlaceFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    def get_linked_places_resource_identifier(self, rel_facade=None):
        rel_facade = PlaceFacade if not rel_facade else rel_facade

        if self.obj.commune_insee_code is None:
            return [] if self.obj.localization_commune is None or self.obj.localization_commune.place is None else [
                rel_facade.make_resource_identifier(lp.id, rel_facade.TYPE)
                for lp in self.obj.localization_commune.place.linked_places if
                lp.commune_insee_code is None and lp.id != self.obj.id]
        else:
            return [] if len(self.obj.linked_places) == 0 else [
                rel_facade.make_resource_identifier(lp.id, rel_facade.TYPE)
                for lp in self.obj.linked_places if
                lp.commune_insee_code is None]

    def get_linked_places_resource(self, rel_facade=None):
        rel_facade = PlaceFacade if not rel_facade else rel_facade

        if self.obj.commune_insee_code is None:
            return [] if self.obj.localization_commune is None or self.obj.localization_commune.place is None else [rel_facade(self.url_prefix, lp,
                                                                                 self.with_relationships_links,
                                                                                 self.with_relationships_data).resource
                                                                     for lp in
                                                                     self.obj.localization_commune.place.linked_places
                                                                     if
                                                                     lp.commune_insee_code is None and lp.id != self.obj.id]
        else:
            return [] if len(self.obj.linked_places) == 0 else [rel_facade(self.url_prefix, lp,
                                                                            self.with_relationships_links,
                                                                            self.with_relationships_data).resource
                                                                for lp in self.obj.linked_places if
                                                                lp.commune_insee_code is None]

    @property
    def resource(self):
        """Make a JSONAPI resource object describing what is a dictionnary place
        A dictionnary place is made of:
        attributes:
        relationships:
        Returns
        -------
            A dict describing the corresponding JSONAPI resource object
        """

        res = {
            **self.resource_identifier,
            "attributes": {
                "label": self.obj.label,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "localization-commune-relation-type": self.obj.localization_commune_relation_type,
                "localization-insee-code": self.obj.related_commune.id if self.obj.related_commune else None,

                'geoname-id': self.obj.commune.geoname_id if self.obj.commune else None,
                'wikidata-item-id': self.obj.commune.wikidata_item_id if self.obj.commune else None,
                'wikipedia-url': self.obj.commune.wikipedia_url if self.obj.commune else None,
                'databnf-ark': self.obj.commune.databnf_ark if self.obj.commune else None,
                'viaf-id': self.obj.commune.viaf_id if self.obj.commune else None,
                'siaf-id': self.obj.commune.siaf_id if self.obj.commune else None,
                'osm-id': self.obj.commune.osm_id if self.obj.commune else None,
                'inha-uri': 'https://thesaurus.inha.fr/thesaurus/page/ark:/54721/{0}'.format(
                    self.obj.commune.inha_uuid) if self.obj.commune else None,
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
        super(PlaceFacade, self).__init__(*args, **kwargs)

        from app.api.insee_commune.facade import CommuneFacade
        from app.api.place_old_label.facade import PlaceOldLabelFacade
        from app.api.responsibility.facade import ResponsibilityFacade
        from app.api.place_description.facade import PlaceDescriptionFacade
        from app.api.place_comment.facade import PlaceCommentFacade

        self.relationships = {
            "linked-places": {
                "links": self._get_links(rel_name="linked-places"),
                "resource_identifier_getter": self.get_linked_places_resource_identifier,
                "resource_getter": self.get_linked_places_resource
            },
        }

        for rel_name, (rel_facade, to_many) in {
            "responsibility": (ResponsibilityFacade, False),
            "commune": (CommuneFacade, False),
            "localization-commune": (CommuneFacade, False),
            "descriptions": (PlaceDescriptionFacade, True),
            "comments": (PlaceCommentFacade, True),
            "old-labels": (PlaceOldLabelFacade, True),
            "place-feature-types": (PlaceFeatureTypeFacade, True)

        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }

    def get_data_to_index_when_added(self, propagate):
        co = self.obj.related_commune

        payload = {
            "id": self.obj.id,
            "place-id": self.obj.id,
            "type": self.TYPE,

            "label": self.obj.label,
            "place-label": self.obj.label,
            "localization-insee-code": co.id if co else None,
            "commune-label": co.NCCENR if co else None,

            "dep-id": self.obj.dpt,
            "ctn-id": co.canton.id if co and co.canton else None,
            "reg-id": co.region.insee_code if co and co.region else None,

            "ctn-label": co.canton.label if co and co.canton else None,
        }

        return [
            {"id": self.obj.id, "index": self.get_index_name(), "payload": payload},
        ]

    def get_data_to_index_when_removed(self, propagate):
        print("GOING TO BE REMOVED FROM INDEX:", [{"id": self.obj.id, "index": self.get_index_name()}])
        return [
            {"id": self.obj.id, "index": self.get_index_name()},
        ]


class PlaceSearchFacade(PlaceFacade):

    @property
    def resource(self):
        """ """
        from app.api.place_description.facade import PlaceDescriptionFacade
        co = self.obj.related_commune

        old_labels = []
        for o in self.obj.old_labels:
            if o.rich_date:
                old_labels.append("{0} ({1})".format(o.rich_label, o.rich_date))
            else:
                old_labels.append(o.rich_label)

        old_labels.reverse()

        res = {
            **self.resource_identifier,
            "attributes": {
                "place-id": self.obj.id,
                "place-label": self.obj.label,
                "old-labels": old_labels,
                "localization-insee-code": co.id if co else None,
                "commune-label": co.NCCENR if co else None,
                "dpt": self.obj.dpt,
                "canton": co.canton.label if co and co.canton else None,
                "region": co.region.label if co and co.region else None,
                "longlat": co.longlat if co else None,
                "descriptions": [d.resource["attributes"]["content"]
                                 for d in [PlaceDescriptionFacade("", e)
                                           for e in self.obj.descriptions]]
            },
            "links": {
                "self": self.self_link
            }
        }
        return res


class PlaceMapFacade(PlaceSearchFacade):

    @property
    def resource(self):
        """ """
        co = self.obj.related_commune
        res = {
            **self.resource_identifier,
            "attributes": {
                "place-label": self.obj.label,
                "localization-insee-code": co.id if co else None,
                "longlat": co.longlat if co else None,

                "dpt": "{0} - {1}".format(co.departement.insee_code, co.departement.label) if co and co.departement else None,
                "region": "{0} - {1}".format(co.region.insee_code, co.region.label) if co and co.region else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res


class LinkedPlaceFacade(PlaceSearchFacade):

    @property
    def resource(self):
        """ """
        from app.api.place_description.facade import PlaceDescriptionFacade

        res = {
            **self.resource_identifier,
            "attributes": {
                "place-label": self.obj.label,
                #"responsibility": self.obj.responsibility,
                "descriptions": [d.resource["attributes"]["content"]
                                 for d in [PlaceDescriptionFacade("", e)
                                 for e in self.obj.descriptions]]
            },
            "links": {
                "self": self.self_link
            }
        }
        return res
