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
        return None if self.obj.placename is None else PlacenameFacade.make_resource_identifier(self.obj.placename.id, PlacenameFacade.TYPE)

    def get_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade

        return None if (self.obj.placename or self.obj.placename.commune is None) else CommuneFacade.make_resource_identifier(self.obj.placename.commune.id, CommuneFacade.TYPE)

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
