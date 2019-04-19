from flask_jwt_extended import get_jwt_identity, get_jwt_claims, jwt_required, verify_jwt_in_request
from functools import wraps
from app import JSONAPIResponseFactory
from flask import request

from app.api.route_registrar import json_loads


error_401 = JSONAPIResponseFactory.make_errors_response(
    {
        "status": 401,
        "title": "Unauthorized"
    },
    status=401
)


def error_403(s):
    return JSONAPIResponseFactory.make_errors_response(
        {
            "status": 403,
            "title": "Forbidden",
            "detail": s
        },
        status=403
        )


def api_require_roles(*required_roles):
    def wrap(view_function):
        @wraps(view_function)
        def wrapped_f(*args, **kwargs):
            verify_jwt_in_request()
            ret = {
                'current_identity': get_jwt_identity(),  # username
                'current_roles': get_jwt_claims()  # roles
            }
            print("You are", ret)
            print("You need to be", required_roles)
            for required_role in required_roles:
                if required_role not in ret["current_roles"]:
                    print("Sorry, you are not '" + required_role + "'")
                    return error_401
            res = view_function(*args, **kwargs)
            return res

        return wrapped_f

    return wrap


from app.api.placename.decorators.exports.linkedplaces import export_placename_to_linkedplace

export_funcs = {
    # the export format will be available under this http parameter value.
    # ex: http://localhost:5003/dico-topo/api/1.0/placenames?page[size]=200&without-relationships&export=linkedplacename
    #     or
    #     http://localhost:5003/dico-topo/api/1.0/placenames/DT02-02878?export=linkedplacename
    "linkedplacename": export_placename_to_linkedplace
}


def export_to(export_format):
    def wrap(view_function):
        @wraps(view_function)
        def wrapped_f(*args, **kwargs):
            response = view_function(*args, **kwargs)
            if "export" in request.args:
                asked_format = request.args["export"]
                if asked_format not in export_funcs or export_format not in export_funcs:
                    raise ValueError('export format unknown or unavailable')
                func = export_funcs[asked_format]
                try:
                    data = json_loads(response.data)
                    output_data, status, headers, content_type = func(request, data)
                    response = JSONAPIResponseFactory.make_response(
                        resource=output_data,
                        status=status,
                        headers=headers,
                        content_type=content_type
                    )
                except Exception as e:
                    return error_403(str(e))
            return response

        return wrapped_f

    return wrap




