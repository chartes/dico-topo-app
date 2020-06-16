from app.api.abstract_facade import JSONAPIAbstractFacade


class PlaceFeatureTypeFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "place-feature-type"
    TYPE_PLURAL = "place-feature-types"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import PlaceFeatureType

        e = PlaceFeatureType.query.filter(PlaceFeatureType.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlaceFeatureType %s does not exist" % id}]
        else:
            e = PlaceFeatureTypeFacade(url_prefix, e, **kwargs)
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
        super(PlaceFeatureTypeFacade, self).__init__(*args, **kwargs)
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
