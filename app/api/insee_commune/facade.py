from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.insee_ref.facade import InseeRefFacade


class CommuneFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "commune"
    TYPE_PLURAL = "communes"

    @property
    def id(self):
        return self.obj.insee_id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

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
    def region(self):
        return self.obj.region

    @property
    def departement(self):
        return self.obj.departement

    @property
    def arrondissement(self):
        return self.obj.arrondissement

    @property
    def canton(self):
        return self.obj.canton

    @property
    def region_resource_identifier(self):
        return None if self.region is None else InseeRefFacade(self.region).resource_identifier

    @property
    def departement_resource_identifier(self):
        return None if self.departement is None else InseeRefFacade(self.departement).resource_identifier

    @property
    def arrondissement_resource_identifier(self):
        return None if self.arrondissement is None else InseeRefFacade(self.arrondissement).resource_identifier

    @property
    def canton_resource_identifier(self):
        return None if self.canton is None else InseeRefFacade(self.canton).resource_identifier

    @property
    def region_resource(self):
        return None if self.region is None else InseeRefFacade(self.region).resource

    @property
    def departement_resource(self):
        return None if self.departement is None else InseeRefFacade(self.departement).resource

    @property
    def arrondissement_resource(self):
        return None if self.arrondissement is None else InseeRefFacade(self.arrondissement).resource

    @property
    def canton_resource(self):
        return None if self.canton is None else InseeRefFacade(self.canton).resource

    @property
    def relationships(self):
        return {
            "region": {
                "links": self.links_reg,
                "resource_identifier": self.region_resource_identifier,
                "resource": self.region_resource
            },
            "departement": {
                "links": self.links_dep,
                "resource_identifier": self.departement_resource_identifier,
                "resource": self.departement_resource
            },
            "arrondissement": {
                "links": self.links_ar,
                "resource_identifier": self.arrondissement_resource_identifier,
                "resource": self.arrondissement_resource
            },
            "canton": {
                "links": self.links_ct,
                "resource_identifier": self.canton_resource_identifier,
                "resource": self.canton_resource
            }
        }

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
            "relationships": self._exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
