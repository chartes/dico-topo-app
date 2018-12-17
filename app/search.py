import pprint
from elasticsearch.helpers import scan
from flask import current_app
from collections import namedtuple

def add_to_index(index, model):
    if not current_app.elasticsearch:
        print("WARNING: elasticsearch not properly configured")
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                    body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        print("WARNING: elasticsearch not properly configured")
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, fields=None, page=None, per_page=None):
    if not current_app.elasticsearch:
        print("WARNING: elasticsearch not properly configured")
        return {}, 0
    body = {
        'query': {
            'query_string': {
                'query': query,
                #'fields': ['*'] if fields is None or len(fields) == 0 else fields
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
        body["from"] = 0
        body["size"] = 10000
        #print("WARNING: /!\ for debug purposes the query size is limited to", body["size"])

    try:
        #search = current_app.elasticsearch.search(index=index, doc_type=index, body=body)
        search = current_app.elasticsearch.search(
            body=body,
            index=index,
            doc_type=index,
            from_=page*per_page,
            size=per_page
        )
        results = {}
        total = search["hits"]["total"]
        for hit in search["hits"]["hits"]:
            _idx = str(hit['_index'])

            if _idx not in results:
                results[_idx] = []

            results[_idx].append({
                "id": str(hit['_id']),
                "score": str(hit['_score'])
            })
        return results, total

    except Exception as e:
        print(e)
        return {}, 0
