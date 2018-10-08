from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.placename.facade import PlacenameFacade


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

    def get_communes(self):
        communes = []
        communes_region = self.obj.communes_region
        communes_canton = self.obj.communes_canton
        communes_departement = self.obj.communes_departement
        communes_arrondissement = self.obj.communes_arrondissement
        if communes_region:
            communes.extend(communes_region)
        if communes_canton:
            communes.extend(communes_canton)
        if communes_departement:
            communes.extend(communes_departement)
        if communes_arrondissement:
            communes.extend(communes_arrondissement)
        return communes

    def get_placenames(self):
        return [p for c in self.get_communes() for p in c.placenames]

    def get_parent_resource_identifier(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource_identifier

    def get_children_resource_identifiers(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource_identifier
                                                     for c in self.obj.children]

    def get_communes_resource_identifiers(self):
        communes = self.get_communes()
        from app.api.insee_commune.facade import CommuneFacade
        return [] if len(communes) == 0 else [CommuneFacade(self.url_prefix, c).resource_identifier for c in communes]

    def get_placenames_resource_identifiers(self):
        placenames = self.get_placenames()
        return [] if len(placenames) == 0 else [PlacenameFacade(self.url_prefix, p).resource_identifier for p in
                                                placenames]

    def get_parent_resource(self):
        return None if self.obj.parent is None else InseeRefFacade(self.url_prefix, self.obj.parent).resource

    def get_children_resource(self):
        return [] if self.obj.children is None else [InseeRefFacade(self.url_prefix, c).resource
                                                     for c in self.obj.children]

    def get_communes_resource(self):
        communes = self.get_communes()
        from app.api.insee_commune.facade import CommuneFacade
        return [] if len(communes) == 0 else [CommuneFacade(self.url_prefix, c).resource for c in communes]

    def get_placenames_resource(self):
        placenames = self.get_placenames()
        return [] if len(placenames) == 0 else [PlacenameFacade(self.url_prefix, p).resource for p in placenames]

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
            },
            "communes": {
                "links": self._get_links(rel_name="communes"),
                "resource_identifier_getter": self.get_communes_resource_identifiers,
                "resource_getter": self.get_communes_resource
            },
            "placenames": {
                "links": self._get_links(rel_name="placenames"),
                "resource_identifier_getter": self.get_placenames_resource_identifiers,
                "resource_getter": self.get_placenames_resource
            }
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'id': self.obj.id,
                'reference-type': self.obj.type,
                'insee-code': self.obj.insee_code,
                'level': self.obj.level,
                'label': self.obj.label
            },
            "relationships": self.get_exposed_relationships(),
            "meta": self.meta,
            "links": {
                "self": self.self_link
            }
        }


