from app.api.abstract_facade import JSONAPIAbstractFacade


class BiblFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "bibl"
    TYPE_PLURAL = "bibls"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import Bibl

        e = Bibl.query.filter(Bibl.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "Bibl %s does not exist" % id}]
        else:
            e = BiblFacade(url_prefix, e, **kwargs)
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
                "abbr": self.obj.abbr,
                "bibl": self.obj.bibl,
                "bnf_catalogue_ark": self.obj.bnf_catalogue_ark,
                "gallica_ark": self.obj.gallica_ark,
                "gallica_page_one": self.obj.gallica_page_one,
                "gallica_IIIF_availability": self.obj.gallica_IIIF_availability
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
        super(BiblFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a Bibl
        """

        self.relationships = {
        }

        from app.api.place.facade import PlaceFacade
        for rel_name, (rel_facade, to_many) in {
            "places": (PlaceFacade, True)
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }
