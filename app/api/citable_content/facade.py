from app.api.abstract_facade import JSONAPIAbstractFacade


class CitableContentFacade(JSONAPIAbstractFacade):
    """

    """
    @property
    def id(self):
        return self.obj.id

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                "content": self.obj.content
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
        super(CitableContentFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a CitableContentFacade
        """

        self.relationships = {
        }

        from app.api.responsibility.facade import ResponsibilityFacade

        for rel_name, (rel_facade, to_many) in {
            "responsibility": (ResponsibilityFacade, False)
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }
