from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.entry.facade import EntryFacade


class OldOrthFacade(JSONAPIAbstractFacade):
    """

    """

    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return "old-orth"

    @property
    def type_plural(self):
        return "old-orths"

    @property
    def links_entry(self):
        return self._get_links(rel_name="entry")

    @property
    def links_old_orths(self):
        return self._get_links(rel_name="old-orths")

    @property
    def entry_resource_identifier(self):
        from app.api.entry.facade import EntryFacade
        return None if self.obj.entry is None else EntryFacade(self.obj.entry).resource_identifier

    @property
    def old_orths_resource_identifiers(self):
        return [] if self.obj.entry is None else EntryFacade(self.obj.entry).old_orths_resource_identifiers

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "orth": self.obj.old_orth,
                "date-rich": self.obj.date_rich,
                "date-nude": self.obj.date_nude,
                "reference-rich": self.obj.date_rich,
                "reference-nude": self.obj.date_nude
            },
            "relationships": {
                "entry": {
                    **self.links_entry,
                    "data": self.entry_resource_identifier
                },
                "old-orths": {
                    **self.links_old_orths,
                    "data": self.old_orths_resource_identifiers
                }
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
