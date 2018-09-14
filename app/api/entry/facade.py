from flask import current_app
from app.api.abstract_facade import JSONAPIAbstractFacade


class EntryFacade(JSONAPIAbstractFacade):

    """

    """
    TYPE = "entry"
    TYPE_PLURAL = "entries"

    @property
    def id(self):
        return self.obj.entry_id

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
    def links_alt_orths(self):
        return self._get_links("alt-orths")

    @property
    def links_old_orths(self):
        return self._get_links("old-orths")

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
    def alt_orths(self):
        return self.obj.alt_orths

    @property
    def old_orths(self):
        return self.obj.old_orths

    @property
    def commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.commune is None else CommuneFacade(self.commune).resource_identifier

    @property
    def linked_commune_resource_identifier(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.localization_commune is None else CommuneFacade(self.localization_commune).resource_identifier

    @property
    def linked_placenames_resource_identifiers(self):
        return [] if self.localization_placename is None else [EntryFacade(_loc).resource_identifier
                                                               for _loc in self.localization_placename]

    @property
    def alt_orths_resource_identifiers(self):
        from app.api.alt_orth.facade import AltOrthFacade
        return [] if self.alt_orths is None else [AltOrthFacade(_as).resource_identifier for _as in self.alt_orths]

    @property
    def old_orths_resource_identifiers(self):
        from app.api.old_orth.facade import OldOrthFacade
        return [] if self.old_orths is None else [OldOrthFacade(_os).resource_identifier for _os in self.old_orths]

    @property
    def commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.commune is None else CommuneFacade(self.commune).resource

    @property
    def linked_commune_resource(self):
        from app.api.insee_commune.facade import CommuneFacade
        return None if self.localization_commune is None else CommuneFacade(self.localization_commune).resource

    @property
    def linked_placenames_resources(self):
        return [] if self.localization_placename is None else [EntryFacade(_loc).resource
                                                               for _loc in self.localization_placename]

    @property
    def alt_orths_resources(self):
        from app.api.alt_orth.facade import AltOrthFacade
        return [] if self.alt_orths is None else [AltOrthFacade(_as).resource for _as in self.alt_orths]

    @property
    def old_orths_resources(self):
        from app.api.old_orth.facade import OldOrthFacade
        return [] if self.old_orths is None else [OldOrthFacade(_os).resource for _os in self.old_orths]

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
            "alt-orths": {
                "links": self.links_alt_orths,
                "resource_identifier": self.alt_orths_resource_identifiers,
                "resource": self.alt_orths_resource_identifiers
            },
            "old-orths": {
                "links": self.links_old_orths,
                "resource_identifier": self.old_orths_resource_identifiers,
                "resource": self.old_orths_resources
            },
        }

    @property
    def resource(self):
        """Make a JSONAPI resource object describing what is a dictionnary entry

        A dictionnary entry is made of:
        attributes:
            orth:
            country:
            dpt:
            def:
            start_pg:
            localization-certainty:
        relationships:

        Returns
        -------
            A dict describing the corresponding JSONAPI resource object
        """
        return {
            **self.resource_identifier,
            "attributes": {
                "orth": self.obj.orth,
                "country": self.obj.country,
                "dpt": self.obj.dpt,
                "def": self.obj.def_col,
                "start-page": self.obj.start_pg,
                "localization-certainty": self.obj.localization_certainty
            },
            "relationships": self._exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
