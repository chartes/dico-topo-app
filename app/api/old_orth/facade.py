from app.api.abstract_facade import JSONAPIAbstractFacade


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
                    "data": None if self.obj.entry is None else self.obj.entry.resource_identifier
                },
                "old-orths": {
                    **self.links_old_orths,
                    "data": [OldOrthFacade(os).resource_identifier for os in self.obj.entry.old_orths]
                }
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
