from app import JSONAPIResponseFactory, api_bp


class JSONAPIRuleRegistrar(object):
    """

    """

    def __init__(self, api_version, url_prefix):
        self.api_version = api_version
        self.url_prefix = url_prefix

    def register_get_routes(self, obj_getter, model, facade_class):
        """

        :param model:
        :param facade_class:
        :param obj_getter:
        :param facade:
        :return:
        """

        # =======================
        # Collection GET route
        # =======================
        get_collection_rule = '/api/{api_version}/{type_plural}'.format(
            api_version=self.api_version,
            type_plural=facade_class.TYPE_PLURAL
        )

        def collection_endpoint():
            all_objs = model.query.all()
            return JSONAPIResponseFactory.make_data_response(
                [facade_class(self.url_prefix, obj).resource for obj in all_objs]
            )

        collection_endpoint.__name__ = "%s_%s" % (facade_class.TYPE_PLURAL, collection_endpoint.__name__)
        # register the rule
        api_bp.add_url_rule(get_collection_rule, endpoint=collection_endpoint.__name__, view_func=collection_endpoint)

        # =======================
        # Obj GET route
        # =======================
        single_obj_rule = '/api/{api_version}/{type_plural}/<id>'.format(
            api_version=self.api_version,
            type_plural=facade_class.TYPE_PLURAL
        )

        def single_obj_endpoint(id):
            obj, kwargs, errors = obj_getter(id)
            if obj is None:
                return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
            else:
                f_placename = facade_class(self.url_prefix, obj)
                return JSONAPIResponseFactory.make_data_response(f_placename.resource)

        single_obj_endpoint.__name__ = "%s_%s" % (facade_class.TYPE_PLURAL, single_obj_endpoint.__name__)
        # register the rule
        api_bp.add_url_rule(single_obj_rule, endpoint=single_obj_endpoint.__name__, view_func=single_obj_endpoint)

    def register_relationship_get_route(self, obj_getter, facade_class, rel_name):
        """

        :param obj_getter:
        :param facade_class:
        :param rel_name:
        :return:
        """
        # ===============================
        # relationships self link route
        # ===============================
        rule = '/api/{api_version}/{type_plural}/<id>/relationships/{rel_name}'.format(
            api_version=self.api_version,
            type_plural=facade_class.TYPE_PLURAL, rel_name=rel_name
        )

        def resource_identifier_endpoint(id):
            obj, kwargs, errors = obj_getter(id)
            if obj is None:
                return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
            else:
                relationship = facade_class(self.url_prefix, obj).relationships[rel_name]
                data = {"links": relationship["links"], "data": relationship["resource_identifier"]}
                return JSONAPIResponseFactory.make_response(data, **kwargs)

        resource_identifier_endpoint.__name__ = "%s_%s_%s" % (
            facade_class.TYPE_PLURAL, rel_name.replace("-", "_"), resource_identifier_endpoint.__name__
        )
        # register the rule
        api_bp.add_url_rule(rule, endpoint=resource_identifier_endpoint.__name__, view_func=resource_identifier_endpoint)

        # ===================================
        # relationships related link route
        # ===================================
        rule = '/api/{api_version}/{type_plural}/<id>/{rel_name}'.format(
            api_version=self.api_version,
            type_plural=facade_class.TYPE_PLURAL, rel_name=rel_name
        )

        def resource_endpoint(id):
            obj, kwargs, errors = obj_getter(id)
            if obj is None:
                return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
            else:
                relationship = facade_class(self.url_prefix, obj).relationships[rel_name]
                return JSONAPIResponseFactory.make_data_response(relationship["resource"])

        resource_endpoint.__name__ = "%s_%s_%s" % (
            facade_class.TYPE_PLURAL, rel_name.replace("-", "_"), resource_endpoint.__name__)
        # register the rule
        api_bp.add_url_rule(rule, endpoint=resource_endpoint.__name__, view_func=resource_endpoint)
