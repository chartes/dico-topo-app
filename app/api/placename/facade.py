from app.api.abstract_facade import JSONAPIAbstractFacade


class PlacenameFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "placename"
    TYPE_PLURAL = "placenames"

    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    def get_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.obj.commune is None else CommuneFacade(self.url_prefix, self.obj.commune).resource_identifier

    def get_localization_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.obj.localization_commune is None else CommuneFacade(self.url_prefix, self.obj.localization_commune).resource_identifier

    def get_localization_placename_resource_identifier(self):
        return None if self.obj.localization_placename is None else PlacenameFacade(self.url_prefix,  self.obj.localization_placename).resource_identifier

    def get_alt_labels_resource_identifiers(self):
        from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
        return [] if self.obj.alt_labels is None else [PlacenameAltLabelFacade(self.url_prefix, _as).resource_identifier
                                                       for _as in self.obj.alt_labels]

    def get_old_labels_resource_identifiers(self):
        from app.api.placename_old_label.facade import PlacenameOldLabelFacade
        return [] if self.obj.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, _os).resource_identifier
                                                       for _os in self.obj.old_labels]

    def get_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.obj.commune is None else CommuneFacade(self.url_prefix, self.obj.commune,
                                                                                self.with_relationships_links,
                                                                                self.with_relationships_data).resource

    def get_localization_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.obj.localization_commune is None else CommuneFacade(self.url_prefix,
                                                                                self.obj.localization_commune,
                                                                                self.with_relationships_links,
                                                                                self.with_relationships_data).resource

    def get_localization_placename_resources(self):
        return None if self.obj.localization_placename is None else PlacenameFacade(self.url_prefix, self.obj.localization_placename,
                                                                                self.with_relationships_links,
                                                                                self.with_relationships_data).resource

    def get_alt_labels_resources(self):
        from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
        return [] if self.obj.alt_labels is None else [PlacenameAltLabelFacade(self.url_prefix, _as,
                                                                                self.with_relationships_links,
                                                                                self.with_relationships_data).resource
                                                       for _as in self.obj.alt_labels]

    def get_old_labels_resources(self):
        from app.api.placename_old_label.facade import PlacenameOldLabelFacade
        return [] if self.obj.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, _os,
                                                                                self.with_relationships_links,
                                                                                self.with_relationships_data).resource
                                                       for _os in self.obj.old_labels]

    @property
    def relationships(self):
        return {
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
            "localization-placename": {
                "links": self._get_links(rel_name="localization-placename"),
                "resource_identifier_getter": self.get_localization_placename_resource_identifier,
                "resource_getter": self.get_localization_placename_resources
            },
            "alt-labels": {
                "links": self._get_links(rel_name="alt-labels"),
                "resource_identifier_getter": self.get_alt_labels_resource_identifiers,
                "resource_getter": self.get_alt_labels_resources
            },
            "old-labels": {
                "links": self._get_links(rel_name="old-labels"),
                "resource_identifier_getter": self.get_old_labels_resource_identifiers,
                "resource_getter": self.get_old_labels_resources
            },
        }

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
                "id": self.obj.id,
                "label": self.obj.label,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "desc": self.obj.desc,
                "num-start-page": self.obj.num_start_page,
                "localization-certainty": self.obj.localization_certainty,
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
