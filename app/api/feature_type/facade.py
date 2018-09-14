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

    @property
    def links_placename(self):
        return self._get_links(rel_name="placename")

    @property
    def placename_resource_identifier(self):
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix, self.obj.placename).resource_identifier

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "term": self.obj.term
            },
            "relationships": {
                "placename": {
                    **self.links_placename,
                    "data": self.placename_resource_identifier
                },
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }