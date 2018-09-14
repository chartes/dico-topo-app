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

    @property
    def links_parent(self):
        return self._get_links(rel_name="parent")

    @property
    def links_children(self):
        return self._get_links(rel_name="children")

    @property
    def parent_resource_identifier(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource_identifier

    @property
    def children_resource_identifiers(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource_identifier for c in self.obj.children]

    @property
    def parent_resource(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource

    @property
    def children_resource(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource for c in self.obj.children]

    @property
    def relationships(self):
        return {
            #"parent": {
            #    "links": self.links_parent,
            #    "resource_identifier": self.parent_resource_identifier,
            #    "resource": self.parent_resource
            #},
            #"children": {
            #    "links": self.links_children,
            #    "resource_identifier": self.children_resource_identifiers,
            #    "resource": self.children_resource
            #}
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
            "relationships": self._exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }


