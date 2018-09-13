from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.entry.facade import EntryFacade


class KeywordFacade(JSONAPIAbstractFacade):
    """

    """

    @property
    def id(self):
        return "%s_%s" % (self.obj.entry_id, self.obj.term)

    @property
    def type(self):
        return "keyword"

    @property
    def type_plural(self):
        return "keywords"

    @property
    def links_entry(self):
        return self._get_links(rel_name="entry")

    @property
    def entry_resource_identifier(self):
        return None if self.obj.entry is None else EntryFacade(self.obj.entry).resource_identifier

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "term": self.obj.term
            },
            "relationships": {
                "entry": {
                    **self.links_entry,
                    "data": self.entry_resource_identifier
                },
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }