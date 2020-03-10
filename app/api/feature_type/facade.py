from app.api.abstract_facade import JSONAPIAbstractFacade


class FeatureTypeFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "feature-type"
    TYPE_PLURAL = "feature-types"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import FeatureType

        e = FeatureType.query.filter(FeatureType.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "FeatureType %s does not exist" % id}]
        else:
            e = FeatureTypeFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                #"id": self.obj.id,
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

    def __init__(self, *args, **kwargs):
        super(FeatureTypeFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a Feature Type
        """

        from app.api.place.facade import PlaceFacade
        self.relationships = {
            "place": {
                "links": self._get_links(rel_name="place"),
                "resource_identifier_getter": self.get_related_resource_identifiers(PlaceFacade, "place"),
                "resource_getter": self.get_related_resources(PlaceFacade, "place"),
            }
        }
