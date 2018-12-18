from app.api.abstract_facade import JSONAPIAbstractFacade


class PlacenameFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "placename"
    TYPE_PLURAL = "placenames"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import Placename

        e = Placename.query.filter(Placename.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "Placename %s does not exist" % id}]
        else:
            e = PlacenameFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """Make a JSONAPI resource object describing what is a dictionnary placename

        A dictionnary placename is made of:
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

        res = {
            **self.resource_identifier,
            "attributes": {
                "label": self.obj.label,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "desc": self.obj.desc,
                "num-start-page": self.obj.num_start_page,
                "localization-certainty": self.obj.localization_certainty,
                "localization-insee-code": self.obj.commune_insee_code if self.obj.commune_insee_code else self.obj.localization_commune_insee_code,
                "comment": self.obj.comment
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
        super(PlacenameFacade, self).__init__(*args, **kwargs)

        from app.api.insee_commune.facade import CommuneFacade
        from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
        from app.api.placename_old_label.facade import PlacenameOldLabelFacade

        self.relationships = {}

        for rel_name, (rel_facade, to_many) in {
            "commune": (CommuneFacade, False),
            "localization-commune": (CommuneFacade, False),
            "linked-placenames": (PlacenameFacade, True),
            "alt-labels": (PlacenameAltLabelFacade, True),
            "old-labels": (PlacenameOldLabelFacade, True),
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }


class PlacenameSearchFacade(PlacenameFacade):

    @property
    def resource(self):
        """ """
        co = self.obj.localization_commune
        res = {
            **self.resource_identifier,
            "attributes": {
                "placename-id": self.obj.id,
                "placename-label": self.obj.label,
                "localization-insee-code": co.id if co else None,
                "dpt": self.obj.dpt,
                "region": co.region.label if co else None,
                "longlat": co.longlat if co else None,
                "desc": self.obj.desc
            },
            "links": {
                "self": self.self_link
            }
        }
        return res

    def __init__(self, *args, **kwargs):
        super(PlacenameSearchFacade, self).__init__(*args, **kwargs)
        self.relationships = {}


class PlacenameMapFacade(PlacenameSearchFacade):

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
                "localization-insee-code": co.id if co else None,
                "longlat": co.longlat if co else None,
            },
            "links": {
                "self": self.self_link
            }
        }
        return res