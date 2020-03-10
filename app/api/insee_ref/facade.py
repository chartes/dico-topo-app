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

    #def get_communes(self):
    #    communes = []
    #    communes_region = self.obj.communes_region
    #    communes_canton = self.obj.communes_canton
    #    communes_departement = self.obj.communes_departement
    #    communes_arrondissement = self.obj.communes_arrondissement
    #    if communes_region:
    #        communes.extend(communes_region)
    #    if communes_canton:
    #        communes.extend(communes_canton)
    #    if communes_departement:
    #        communes.extend(communes_departement)
    #    if communes_arrondissement:
    #        communes.extend(communes_arrondissement)
    #    return communes
    #
    #def get_places(self):
    #    return [p for c in self.get_communes() for p in c.places]

    #def get_communes_resource_identifiers(self):
    #    communes = self.get_communes()
    #    from app.api.insee_commune.facade import CommuneFacade
    #    return [] if len(communes) == 0 else [CommuneFacade(self.url_prefix, c).resource_identifier for c in communes]
    #
    #def get_places_resource_identifiers(self):
    #    places = self.get_places()
    #    return [] if len(places) == 0 else [PlaceFacade(self.url_prefix, p).resource_identifier for p in
    #                                            places]

    #def get_communes_resource(self):
    #    communes = self.get_communes()
    #    from app.api.insee_commune.facade import CommuneFacade
    #    return [] if len(communes) == 0 else [CommuneFacade(self.url_prefix, c,
    #                                                        self.with_relationships_links,
    #                                                        self.with_relationships_data).resource for c in communes]
    #
    #def get_places_resource(self):
    #    places = self.get_places()
    #    return [] if len(places) == 0 else [PlaceFacade(self.url_prefix, p,
    #                                                            self.with_relationships_links,
    #                                                            self.with_relationships_data).resource
    #                                            for p in places]


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
