from copy import copy

from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.feature_type.facade import FeatureTypeFacade
import re

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

    def get_linked_places_resource_identifier(self):
        if self.obj.commune_insee_code is None:
            return [] if self.obj.localization_commune is None else [ PlaceFacade.make_resource_identifier(self.obj.localization_commune.place.id, PlaceFacade.TYPE)]
        else:
            return [] if len(self.obj.linked_places) == 0 else [PlaceFacade.make_resource_identifier(lp.id, PlaceFacade.TYPE)
                                                                for lp in self.obj.linked_places if
                                                                lp.commune_insee_code is None]

    def get_linked_places_resource(self):
        if self.obj.commune_insee_code is None:
            return [] if self.obj.localization_commune is None else [PlaceFacade(self.url_prefix,
                                                                                 self.obj.localization_commune.place,
                                                                                 self.with_relationships_links,
                                                                                 self.with_relationships_data).resource]
        else:
            return [] if len(self.obj.linked_places) == 0 else [PlaceFacade(self.url_prefix, lp,
                                                                   self.with_relationships_links,
                                                                   self.with_relationships_data).resource
                                                                for lp in self.obj.linked_places if lp.commune_insee_code is None]

    @property
    def resource(self):
        """Make a JSONAPI resource object describing what is a dictionnary place
        A dictionnary place is made of:
        attributes:
            label:
            country:
            dpt:
            desc:
            num-start-page:
            localization-certainty:
            comment:
        relationships:
        Returns
        -------
            A dict describing the corresponding JSONAPI resource object
        """
        if self.obj.commune:
            co = self.obj.commune
        elif self.obj.localization_commune:
            co = self.obj.localization_commune
        else:
            co = None

        res = {
            **self.resource_identifier,
            "attributes": {
                "label": self.obj.label,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "desc": self.obj.desc,
                "comment": self.obj.comment,

                "num-start-page": self.obj.num_start_page,
                "localization-certainty": self.obj.localization_certainty,
                "localization-insee-code": co.id if co else None,

                'geoname-id': co.geoname_id if co else None,
                'wikidata-item-id': co.wikidata_item_id if co else None,
                'wikipedia-url': co.wikipedia_url if co else None,
                'databnf-ark': co.databnf_ark if co else None,
                'viaf-id': co.viaf_id if co else None,
                'siaf-id': co.siaf_id if co else None,
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
        from app.api.place_alt_label.facade import PlaceAltLabelFacade
        from app.api.place_old_label.facade import PlaceOldLabelFacade

        self.relationships = {
            "linked-places": {
                "links": self._get_links(rel_name="linked-places"),
                "resource_identifier_getter": self.get_linked_places_resource_identifier,
                "resource_getter": self.get_linked_places_resource
            },
        }

        for rel_name, (rel_facade, to_many) in {
            "commune": (CommuneFacade, False),
            "localization-commune": (CommuneFacade, False),
            "alt-labels": (PlaceAltLabelFacade, True),
            "old-labels": (PlaceOldLabelFacade, True),
            "feature-types": (FeatureTypeFacade, True),
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }

        # rewrite links in desc so they target to a better url
        if self.obj.desc:
            if self.obj.localization_commune_insee_code and self.obj.localization_place_id:
                self.obj.desc = re.sub(r'<a href="{0}">'.format(self.obj.localization_commune_insee_code),
                                       '<a href="/places/{0}">'.format(self.obj.localization_place_id), self.obj.desc)

            # remove unused links to feature types
            self.obj.desc = re.sub(r'<a>(.*?)</a>', r'\1', self.obj.desc)

    def get_data_to_index_when_added(self, propagate):
        if self.obj.commune:
            co = self.obj.commune
        elif self.obj.localization_commune:
            co = self.obj.localization_commune
        else:
            co = None

        payload = {
            "id": self.obj.id,
            "place-id": self.obj.id,
            "type": self.TYPE,

            "label": self.obj.label,
            "place-label": self.obj.label,
            "localization-insee-code": co.id if co else None,
            "commune-label": co.NCCENR if co else None,

            "dep-id": self.obj.dpt,
            "reg-id": co.region.insee_code if co and co.region else None,
            # "old-labels": [ol.rich_label for ol in self.obj.old_labels],
            # "alt-labels": [al.label for al in self.obj.alt_labels]
        }

        #payload_groupby_place = copy(payload)
        #payload_groupby_place["old-labels"] = [ol.rich_label for ol in self.obj.old_labels]

        return [
            {"id": self.obj.id, "index": self.get_index_name(), "payload": payload},
            #{"id": self.obj.id, "index": "{0}_agg".format(self.get_index_name()), "payload": payload_groupby_place}
        ]

    def get_data_to_index_when_removed(self, propagate):
        print("GOING TO BE REMOVED FROM INDEX:", [{"id": self.obj.id, "index": self.get_index_name()}])
        return [
            {"id": self.obj.id, "index": self.get_index_name()},
            #{"id": self.obj.id, "index": "{0}_agg".format(self.get_index_name())}
        ]


class PlaceSearchFacade(PlaceFacade):

    @property
    def resource(self):
        """ """
        if self.obj.commune:
            co = self.obj.commune
        elif self.obj.localization_commune:
            co = self.obj.localization_commune
        else:
            co = None
        res = {
            **self.resource_identifier,
            "attributes": {
                "place-id": self.obj.id,
                "place-label": self.obj.label,
                "old-labels": ["{0} ({1})".format(o.rich_label, o.rich_date) for o in self.obj.old_labels],
                "localization-insee-code": co.id if co else None,
                "commune-label": co.NCCENR if co else None,
                "dpt": self.obj.dpt,
                "region": co.region.label if co else None,
                "longlat": co.longlat if co else None,
                "desc": self.obj.desc,
                "comment": self.obj.comment,
                "num-start-page": self.obj.num_start_page,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res

    def __init__(self, *args, **kwargs):
        super(PlaceSearchFacade, self).__init__(*args, **kwargs)
        #self.relationships = {}


class PlaceMapFacade(PlaceSearchFacade):

    @property
    def resource(self):
        """ """
        if self.obj.commune:
            co = self.obj.commune
        elif self.obj.localization_commune:
            co = self.obj.localization_commune
        else:
            co = None
        res = {
            **self.resource_identifier,
            "attributes": {
                "place-label": self.obj.label,
                "localization-insee-code": co.id if co else None,
                "longlat": co.longlat if co else None,

                "dpt": "{0} - {1}".format(co.departement.insee_code, co.departement.label) if co else None,
                "region": "{0} - {1}".format(co.region.insee_code, co.region.label) if co else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res
