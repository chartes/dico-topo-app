from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.entry.facade import EntryFacade


class AltOrthFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "alt-orth"
    TYPE_PLURAL = "alt-orths"

    @property
    def id(self):
        return "%s_%s" % (self.obj.entry_id, self.obj.alt_orth)

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    @property
    def links_entry(self):
        return self._get_links(rel_name="entry")

    @property
    def entry_resource_identifier(self):
        return None if self.obj.entry is None else EntryFacade(self.obj.entry).resource_identifier

    @property
    def entry_resource(self):
        return None if self.obj.entry is None else EntryFacade(self.obj.entry).resource

    @property
    def relationships(self):
        return {
            "commune": {
                "links": self.links_entry,
                "resource_identifier": self.entry_resource_identifier,
                "resource": self.entry_resource
            }
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "alt_orth": self.obj.alt_orth
            },
            "relationships": self._exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }

