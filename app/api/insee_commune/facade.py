from app.api.abstract_facade import JSONAPIAbstractFacade


class CommuneFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "commune"
    TYPE_PLURAL = "communes"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import InseeCommune

        e = InseeCommune.query.filter(InseeCommune.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "Commune %s does not exist" % id}]
        else:
            e = CommuneFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                'insee-code': self.obj.id,
                'NCCENR': self.obj.NCCENR,
                'ARTMIN': self.obj.ARTMIN,
                'longlat': self.obj.longlat,

                'geoname-id': self.obj.geoname_id,
                'wikidata-item-id': self.obj.wikidata_item_id,
                'wikipedia-url': self.obj.wikipedia_url,
                'databnf-ark': self.obj.databnf_ark,
                'viaf-id': self.obj.viaf_id,
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
        super(CommuneFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a Commune
        """
        from app.api.placename.facade import PlacenameFacade
        from app.api.insee_ref.facade import InseeRefFacade

        self.relationships = {}

        for rel_name, (rel_facade, to_many) in {
            "localized-placenames": (PlacenameFacade, True),
            "placename": (PlacenameFacade, False),
            "region": (InseeRefFacade, False),
            "departement": (InseeRefFacade, False),
            "arrondissement": (InseeRefFacade, False),
            "canton": (InseeRefFacade, False)
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }
