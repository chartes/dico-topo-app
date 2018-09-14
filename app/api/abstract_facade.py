

class JSONAPIAbstractFacade(object):

    """

    """
    TYPE = "ABSTRACT-TYPE"
    TYPE_PLURAL = "ABSTRACT-TYPE-PLURAL"

    def __init__(self, url_prefix, obj):
        self.obj = obj
        self.url_prefix = url_prefix

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
    def self_link(self):
        return "{url_prefix}/{type_plural}/{id}".format(
            url_prefix=self.url_prefix, type_plural=self.type_plural, id=self.id
        )

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": self.type,
            "id": self.id
        }

    @property
    def resource(self):
        raise NotImplementedError

    @property
    def relationships(self):
        raise NotImplementedError

    def _get_links(self, rel_name):
        return {
            "self": "{url_prefix}/{source_col}/{source_id}/relationships/{rel_name}".format(
                url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id, rel_name=rel_name
            ),
            "related": "{url_prefix}/{source_col}/{source_id}/{rel_name}".format(
                url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id, rel_name=rel_name
            )
        }

    def _exposed_relationships(self):
        return {
            rel_name: {
                "links": rel.get("links"),
                "data": rel.get("resource_identifier")
            }
            for rel_name, rel in self.relationships.items()
        }
