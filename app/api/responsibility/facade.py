from app.api.abstract_facade import JSONAPIAbstractFacade


class ResponsibilityFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "responsibility"
    TYPE_PLURAL = "responsibilities"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import Responsibility

        e = Responsibility.query.filter(Responsibility.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "Responsibility %s does not exist" % id}]
        else:
            e = ResponsibilityFacade(url_prefix, e, **kwargs)
            kwargs = {}
            errors = []
        return e, kwargs, errors

    @property
    def resource(self):
        """ """
        res = {
            **self.resource_identifier,
            "attributes": {
                "num-start-page": self.obj.num_start_page,
                "creation-date": self.obj.creation_date.strftime("%Y-%m-%d %H:%M:%S")
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
        super(ResponsibilityFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a Responsibility
        """

        self.relationships = {
        }

        from app.api.bibl.facade import BiblFacade
        from app.api.user.facade import UserFacade

        for rel_name, (rel_facade, to_many) in {
            "bibl": (BiblFacade, False),
            "user": (UserFacade, False)
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }


class FlatResponsibilityFacade(ResponsibilityFacade):

    @property
    def resource(self):
        """ """
        from app.api.bibl.facade import BiblFacade
        bibl = BiblFacade("", self.obj.bibl)

        res = {
            **self.resource_identifier,
            "attributes": {
                "num-start-page": self.obj.num_start_page,
                "creation-date": self.obj.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                "user": {
                    "id": self.obj.user.id,
                    "username": self.obj.user.username
                },
                "bibl": {
                    "id": bibl.id,
                    **bibl.resource["attributes"]
                }
            },
            "meta": self.meta,
            "links": {
                "self": self.self_link
            }
        }

        return res
