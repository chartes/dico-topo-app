

class JSONAPIAbstractFacade(object):

    """

    """
    TYPE = "ABSTRACT-TYPE"
    TYPE_PLURAL = "ABSTRACT-TYPE-PLURAL"

    ITEMS_PER_PAGE = 10000

    def __init__(self, url_prefix, obj):
        self.obj = obj
        self.url_prefix = url_prefix

        self.self_link = "{url_prefix}/{type_plural}/{id}".format(
            url_prefix=self.url_prefix, type_plural=self.type_plural, id=self.id
        )

        self.resource_identifier = {
            "type": self.type,
            "id": self.id
        }

        self._links_template = {
            "self": "{url_prefix}/{source_col}/{source_id}/relationships".format(
                    url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id
            ),
            "related": "{url_prefix}/{source_col}/{source_id}".format(
                    url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id
            )
        }

    @property
    def id(self):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError

    @property
    def type_plural(self):
        raise NotImplementedError

    @property
    def resource(self):
        raise NotImplementedError

    @property
    def relationships(self):
        raise NotImplementedError

    def _get_links(self, rel_name):
        return {
            "self": "{template}/{rel_name}".format(template=self._links_template["self"], rel_name=rel_name),
            "related": "{template}/{rel_name}".format(template=self._links_template["related"], rel_name=rel_name)
        }

    def get_exposed_relationships(self):
        return {
            rel_name: {
                "links": rel["links"],
                "data": rel["resource_identifier_getter"]()
            }
            for rel_name, rel in self.relationships.items()
        }
