from app.api.abstract_facade import JSONAPIAbstractFacade


class PlacenameAltLabelFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "placename-alt-label"
    TYPE_PLURAL = "placename-alt-labels"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import PlacenameAltLabel

        e = PlacenameAltLabel.query.filter(PlacenameAltLabel.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "PlacenameAltLabel %s does not exist" % id}]
        else:
            e = PlacenameAltLabelFacade(url_prefix, e, **kwargs)
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
        super(PlacenameAltLabelFacade, self).__init__(*args, **kwargs)
        from app.api.placename.facade import PlacenameFacade

        self.relationships = {
            "placename": {
                "links": self._get_links(rel_name="placename"),
                "resource_identifier_getter": self.get_related_resource_identifiers(PlacenameFacade, "placename"),
                "resource_getter":self.get_related_resources(PlacenameFacade, "placename")
            }
        }
