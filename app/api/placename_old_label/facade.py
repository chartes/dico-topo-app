from app.api.abstract_facade import JSONAPIAbstractFacade
from app.api.placename.facade import PlacenameFacade


class PlacenameOldLabelFacade(JSONAPIAbstractFacade):
    """

    """
    TYPE = "placename-old-label"
    TYPE_PLURAL = "placename-old-labels"
    
    @property
    def id(self):
        return self.obj.id

    @property
    def type(self):
        return self.TYPE

    @property
    def type_plural(self):
        return self.TYPE_PLURAL

    def get_placename_resource_identifier(self):
        from app.api.placename.facade import PlacenameFacade
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix, self.obj.placename).resource_identifier

    def get_old_labels_resource_identifiers(self):
        return [] if self.obj.placename.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, ol).resource_identifier
                                                                 for ol in PlacenameFacade(self.url_prefix, self.obj.placename).obj.old_labels]

    def get_placename_resource(self):
        from app.api.placename.facade import PlacenameFacade
        return None if self.obj.placename is None else PlacenameFacade(self.url_prefix, self.obj.placename).resource

    def get_old_labels_resource(self):
        return [] if self.obj.placename.old_labels is None else [PlacenameOldLabelFacade(self.url_prefix, ol).resource
                                                                 for ol in PlacenameFacade(self.url_prefix, self.obj.placename).obj.old_labels]

    @property
    def relationships(self):
        return {
            "old-labels": {
                "links": self._get_links(rel_name="old-labels"),
                "resource_identifier_getter": self.get_old_labels_resource_identifiers,
                "resource_getter": self.get_old_labels_resource
            },
            "placename": {
                "links": self._get_links(rel_name="placename"),
                "resource_identifier_getter": self.get_placename_resource_identifier,
                "resource_getter": self.get_placename_resource
            }
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "rich-label": self.obj.rich_label,
                "rich-date": self.obj.rich_date,
                "text-date": self.obj.text_date,
                "rich-reference": self.obj.rich_reference,
                "rich-label-node": self.obj.rich_label_node,
                "text-label-node": self.obj.text_label_node
            },
            "relationships": self.get_exposed_relationships(),
            "meta": {},
            "links": {
                "self": self.self_link
            }
        }
