from app.api.abstract_facade import JSONAPIAbstractFacade


class InseeRefFacade(JSONAPIAbstractFacade):
    """

    """

    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return "insee-ref"

    @property
    def type_plural(self):
        return "insee-refs"

    @property
    def links_parent(self):
        return self._get_links(rel_name="parent")

    @property
    def links_children(self):
        return self._get_links(rel_name="children")

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'ref-type': self.type,
                'insee': self.obj.insee,
                'level': self.obj.level,
                'label': self.obj.label
            },
            "relationships": {
                "parent": {
                    **self.links_parent,
                    "data": None if self.obj.parent is None else InseeRefFacade(self.obj.parent).resource_identifier
                },
                "children": {
                    **self.links_children,
                    "data": [] if self.obj.children is None else [InseeRefFacade(c).resource_identifier
                                                                  for c in self.obj.children]
                }
            },
            "meta": {},
            "links": {
                "self": "/insee-refs/%s" % self.id
            }
        }


