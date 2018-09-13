from flask import current_app


class JSONAPIAbstractFacade(object):

    """

    """
    def __init__(self, obj):
        self.obj = obj
        self.url_prefix = current_app.config["API_URL_PREFIX"]

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

    def _get_links(self, rel_name):
        return {
            "links": {
                "self": "{url_prefix}/{source_col}/{source_id}/relationships/{rel_name}".format(
                    url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id, rel_name=rel_name
                ),
                "related": "{url_prefix}/{source_col}/{source_id}/{rel_name}".format(
                    url_prefix=self.url_prefix, source_col=self.type_plural, source_id=self.id, rel_name=rel_name
                )
            }
        }
