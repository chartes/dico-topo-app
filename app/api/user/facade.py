from app.api.abstract_facade import JSONAPIAbstractFacade


class UserFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "user"
    TYPE_PLURAL = "users"

    @property
    def id(self):
        return self.obj.id

    @staticmethod
    def get_resource_facade(url_prefix, id, **kwargs):
        from app.models import User

        e = User.query.filter(User.id == id).first()
        if e is None:
            kwargs = {"status": 404}
            errors = [{"status": 404, "title": "User %s does not exist" % id}]
        else:
            e = UserFacade(url_prefix, e, **kwargs)
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
                "username": self.obj.username
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
        super(UserFacade, self).__init__(*args, **kwargs)
        """Make a JSONAPI resource object describing what is a User
        """

        self.relationships = {
        }

        from app.api.responsibility.facade import ResponsibilityFacade
        for rel_name, (rel_facade, to_many) in {
            "responsibilities": (ResponsibilityFacade, True)
        }.items():
            u_rel_name = rel_name.replace("-", "_")

            self.relationships[rel_name] = {
                "links": self._get_links(rel_name=rel_name),
                "resource_identifier_getter": self.get_related_resource_identifiers(rel_facade, u_rel_name, to_many),
                "resource_getter": self.get_related_resources(rel_facade, u_rel_name, to_many),
            }
