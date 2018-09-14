from flask import current_app
from app.api.abstract_facade import JSONAPIAbstractFacade


class PlacenameFacade(JSONAPIAbstractFacade):

    """

    """
    TYPE = "placename"
    TYPE_PLURAL = "placenames"

    @property
    def id(self):
        return self.obj.placename_id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    @property
    def links_commune(self):
        return self._get_links("commune")

    @property
    def links_linked_commune(self):
        return self._get_links("linked-commune")

    @property
    def links_linked_placenames(self):
        return self._get_links("linked-placenames")

    @property
    def links_alt_labels(self):
        return self._get_links("alt-labels")

    @property
    def links_old_labels(self):
        return self._get_links("old-labels")

    @property
    def commune(self):
        return self.obj.commune

    @property
    def localization_commune(self):
        return self.obj.localization_commune

    @property
    def localization_placename(self):
        return self.obj.localization_placename

    @property
    def alt_labels(self):
        return self.obj.alt_labels

    @property
    def old_labels(self):
        return self.obj.old_labels

    @property
    def commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.commune is None else CommuneFacade(self.url_prefix, self.commune).resource_identifier

    @property
    def linked_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.localization_commune is None else CommuneFacade(self.url_prefix, self.localization_commune).resource_identifier

    @property
    def linked_placenames_resource_identifiers(self):
        return [] if self.localization_placename is None else [PlacenameFacade(self.url_prefix, _loc).resource_identifier
                                                               for _loc in self.localization_placename]

    @property
    def alt_labels_resource_identifiers(self):
        from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
        return [] if self.alt_labels is None else [PlacenameAltLabelFacade(self.url_prefix, _as).resource_identifier
                                                   for _as in self.alt_labels]

    @property
    def old_labels_resource_identifiers(self):
        from app.api.placename_old_label.facade import PlacenameOldLabelFacade
        return [] if self.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, _os).resource_identifier
                                                   for _os in self.old_labels]

    @property
    def commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.commune is None else CommuneFacade(self.url_prefix, self.commune).resource

    @property
    def linked_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.localization_commune is None else CommuneFacade(self.url_prefix, self.localization_commune).resource

    @property
    def linked_placenames_resources(self):
        return [] if self.localization_placename is None else [PlacenameFacade(self.url_prefix, _loc).resource
                                                               for _loc in self.localization_placename]

    @property
    def alt_labels_resources(self):
        from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
        return [] if self.alt_labels is None else [PlacenameAltLabelFacade(self.url_prefix, _as).resource
                                                   for _as in self.alt_labels]

    @property
    def old_labels_resources(self):
        from app.api.placename_old_label.facade import PlacenameOldLabelFacade
        return [] if self.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, _os).resource
                                                   for _os in self.old_labels]

    @property
    def relationships(self):
        return {
            "commune": {
                "links": self.links_commune,
                "resource_identifier": self.commune_resource_identifier,
                "resource": self.commune_resource
            },
            "linked-commune": {
                "links": self.links_linked_commune,
                "resource_identifier": self.linked_commune_resource_identifier,
                "resource": self.linked_commune_resource
            },
            "linked-placenames": {
                "links": self.links_linked_placenames,
                "resource_identifier": self.linked_placenames_resource_identifiers,
                "resource": self.linked_placenames_resources
            },
            "alt-labels": {
                "links": self.links_alt_labels,
                "resource_identifier": self.alt_labels_resource_identifiers,
                "resource": self.alt_labels_resource_identifiers
            },
            "old-labels": {
                "links": self.links_old_labels,
                "resource_identifier": self.old_labels_resource_identifiers,
                "resource": self.old_labels_resources
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
        return {
            **self.resource_identifier,
            "attributes": {
                "label": self.obj.label,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "desc": self.obj.desc,
                "num-start-page": self.obj.num_start_page,
                "localization-certainty": self.obj.localization_certainty,
                "comment": self.obj.comment
            },
            "relationships": self._exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
