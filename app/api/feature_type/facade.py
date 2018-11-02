from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.placename.facade import PlacenameFacade


class FeatureTypeFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "feature-type"
    TYPE_PLURAL = "feature-types"

    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    def get_placename_resource_identifier(self):
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix,
                                                                       self.obj.placename).resource_identifier

    def get_placename_resource(self):
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix, self.obj.placename,
                                                                       self.with_relationships_links,
                                                                       self.with_relationships_data).resource

    @property
    def relationships(self):
        return {
            "placename": {
                "links": self._get_links(rel_name="placename"),
                "resource_identifier_getter": self.get_placename_resource_identifier,
                "resource_getter": self.get_placename_resource
            }
        }

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                "id": self.obj.id,
                "term": self.obj.term
            },
            "meta": self.meta,
            "links": {
                "self": self.self_link
            }
        }

        if self.with_relationships_links:
            res["relationships"] = self.get_exposed_relationships()

        return res
