from app.api.abstract_facade import JSONAPIAbstractFacade


class InseeRefFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "insee-ref"
    TYPE_PLURAL = "insee-refs"

    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    def get_parent_resource_identifier(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource_identifier

    def get_children_resource_identifiers(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource_identifier
                                                     for c in self.obj.children]

    def get_parent_resource(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource

    def get_children_resource(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource
                                                     for c in self.obj.children]

    @property
    def relationships(self):
        return {
            "parent": {
                "links": self._get_links(rel_name="parent"),
                "resource_identifier_getter": self.get_parent_resource_identifier,
                "resource_getter": self.get_parent_resource
            },
            "children": {
                "links": self._get_links(rel_name="children"),
                "resource_identifier_getter": self.get_children_resource_identifiers,
                "resource_getter": self.get_children_resource
            }
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'reference-type': self.obj.type,
                'insee-code': self.obj.insee_code,
                'level': self.obj.level,
                'label': self.obj.label
            },
            "relationships": self.get_exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }


