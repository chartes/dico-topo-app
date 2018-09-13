from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.entry.facade import EntryFacade


class AltOrthFacade(JSONAPIAbstractFacade):
    """

    """

    @property
    def id(self):
        return "%s_%s" % (self.obj.entry_id, self.obj.alt_orth)

    @property
    def type(self):
        return "alt-orth"

    @property
    def type_plural(self):
        return "alt-orths"

    @property
    def links_entry(self):
        return self._get_links(rel_name="entry")

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "alt_orth": self.obj.alt_orth
            },
            "relationships": {
                "entry": {
                    **self.links_entry,
                    "data": None if self.obj.entry is None else EntryFacade(self.obj.entry).resource_identifier
                }
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }

