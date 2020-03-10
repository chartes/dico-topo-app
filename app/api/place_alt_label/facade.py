from app.api.abstract_facade import JSONAPIAbstractFacade


class PlaceAltLabelFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "place-alt-label"
    TYPE_PLURAL = "place-alt-labels"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import PlaceAltLabel

        e = PlaceAltLabel.query.filter(PlaceAltLabel.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlaceAltLabel %s does not exist" % id}]
        else:
            e = PlaceAltLabelFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                "label": self.obj.label
            },
            "relationships": self.get_exposed_relationships(),
            "meta": self.meta,
            "links": {
                "self": self.self_link
            }
        }

        if self.with_relationships_links:
            res["relationships"] = self.get_exposed_relationships()

        return res

    def __init__(self, *args, **kwargs):
        super(PlaceAltLabelFacade, self).__init__(*args, **kwargs)
        from app.api.place.facade import PlaceFacade

        self.relationships = {
            "place": {
                "links": self._get_links(rel_name="place"),
                "resource_identifier_getter": self.get_related_resource_identifiers(PlaceFacade, "place"),
                "resource_getter":self.get_related_resources(PlaceFacade, "place")
            }
        }
