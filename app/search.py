import pprint
from flask import current_app

from app import db


class SearchIndexManager(object):

    @staticmethod
    def query_index(index, query, fields=None, page=None, per_page=None):
        if hasattr(current_app, 'elasticsearch'):
            body = {
                'query': {
                    'query_string': {
                        'query': query,
                        # 'fields': ['collections'] if fields is None or len(fields) == 0 else fields
                    }
                },
            }

            if per_page is not None:
                if page is None:
                    page = 0
                else:
                    page = page - 1  # is it correct ?
                body["from"] = page * per_page
                body["size"] = per_page
            else:
                body["from"] = 0 * per_page
                body["size"] = per_page
                # print("WARNING: /!\ for debug purposes the query size is limited to", body["size"])
            try:
                search = current_app.elasticsearch.search(index=index, doc_type=index, body=body)

                #from elasticsearch import Elasticsearch
                #scan = Elasticsearch.helpers.scan(client=current_app.elasticsearch, index=index, doc_type=index, body=body)

                from collections import namedtuple
                Result = namedtuple("Result", "index id type score")

                results = [Result(str(hit['_index']), str(hit['_id']), str(hit['_source']["type"]),
                                  str(hit['_score']))
                           for hit in search['hits']['hits']]

                print(body, len(results), search['hits']['total'], index)

                return results, search['hits']['total']

            except Exception as e:
                raise e

    @staticmethod
    def add_to_index(index, id, payload):
        #print("ADD_TO_INDEX", index, id)
        current_app.elasticsearch.index(index=index, doc_type=index, id=id, body=payload)

    @staticmethod
    def remove_from_index(index, id):
        #print("REMOVE_FROM_INDEX", index, id)
        current_app.elasticsearch.delete(index=index, doc_type=index, id=id)

    #@staticmethod
    #def reindex_resources(changes):
    #    from app.api.facade_manager import JSONAPIFacadeManager
    #
    #    for target_id, target, op in changes:
    #
    #        facade = JSONAPIFacadeManager.get_facade_class(target)
    #        try:
    #            #print("try to reindex", target)
    #            if op in ('insert', 'update'):
    #                target.id = target_id
    #                f_obj = facade("", target)
    #
    #                #f_obj, kwargs, errors = facade.get_resource_facade("", id=target.id)
    #            else:
    #                target.id = target_id
    #                f_obj = facade("", target)
    #            #print("call to reindex for", target_id, target, op)
    #
    #            f_obj.reindex(op)
    #        except Exception as e:
    #            print("Error while indexing %s:" % target, e)
    #            pass
    #