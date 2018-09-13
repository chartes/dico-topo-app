from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.insee_ref.facade import InseeRefFacade


class CommuneFacade(JSONAPIAbstractFacade):
    """

    """

    @property
    def id(self):
        return self.obj.insee_id

    @property
    def type(self):
        return "commune"

    @property
    def type_plural(self):
        return "communes"

    @property
    def links_reg(self):
        return self._get_links(rel_name="region")

    @property
    def links_dep(self):
        return self._get_links(rel_name="departement")

    @property
    def links_ar(self):
        return self._get_links(rel_name="arrondissement")

    @property
    def links_ct(self):
        return self._get_links(rel_name="canton")

    @property
    def region_resource_identifier(self):
        return None if self.obj.reg is None else InseeRefFacade(self.obj.reg).resource_identifier

    @property
    def departement_resource_identifier(self):
        return None if self.obj.dep is None else InseeRefFacade(self.obj.dep).resource_identifier

    @property
    def arrondissement_resource_identifier(self):
        return None if self.obj.ar is None else InseeRefFacade(self.obj.ar).resource_identifier

    @property
    def canton_resource_identifier(self):
        return None if self.obj.ct is None else InseeRefFacade(self.obj.ct).resource_identifier

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'NCCENR': self.obj.NCCENR,
                'ARTMIN': self.obj.ARTMIN,
                'longlat': self.obj.longlat
            },
            "relationships": {
                "region": {
                    **self.links_reg,
                    "data": self.region_resource_identifier
                },
                "departement": {
                    **self.links_dep,
                    "data": self.departement_resource_identifier
                },
                "arrondissement": {
                    **self.links_ar,
                    "data": self.arrondissement_resource_identifier
                },
                "canton": {
                    **self.links_ct,
                    "data": self.canton_resource_identifier
                }
            },
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
