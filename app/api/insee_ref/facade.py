from app.api.abstract_facade import JSONAPIAbstractFacade


class InseeRefFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "insee-ref"
    TYPE_PLURAL = "insee-refs"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import InseeRef

        e = InseeRef.query.filter(InseeRef.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "InseeRef %s does not exist" % id}]
        else:
            e = InseeRefFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                'reference-type': self.obj.type,
                'insee-code': self.obj.insee_code,
                'level': self.obj.level,
                'label': self.obj.label
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
        super(InseeRefFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a document
        """
        self.relationships = {
            "parent": {
                "links": self._get_links(rel_name="parent"),
                "resource_identifier_getter": self.get_related_resource_identifiers(InseeRefFacade, "parent"),
                "resource_getter":  self.get_related_resources(InseeRefFacade, "parent"),
            },
            "children": {
                "links": self._get_links(rel_name="children"),
                "resource_identifier_getter":  self.get_related_resource_identifiers(InseeRefFacade, "children", True),
                "resource_getter":  self.get_related_resources(InseeRefFacade, "children", True),
            },
            #"communes": {
            #    "links": self._get_links(rel_name="communes"),
            #    "resource_identifier_getter": self.get_communes_resource_identifiers,
            #    "resource_getter": self.get_communes_resource
            #},
            #"places": {
            #    "links": self._get_links(rel_name="places"),
            #    "resource_identifier_getter": self.get_places_resource_identifiers,
            #    "resource_getter": self.get_places_resource
            #}
        }


class InseeRefSearchFacade(InseeRefFacade):

    @property
    def resource(self):
        res = super(InseeRefSearchFacade, self).resource

        if self.obj.type == 'AR':
            res['attributes']['dep-insee-code'] = self.obj.parent.insee_code
        if self.obj.type in ('CT', 'CTNP'):
            res['attributes']['dep-insee-code'] = self.obj.parent.parent.insee_code

        return res
