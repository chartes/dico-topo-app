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


def error_400(s):
    return JSONAPIResponseFactory.make_errors_response(
        {
            "status": 400,
            "title": "Bad request",
            "detail": s
        },
        status=400
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


def export_to(export_funcs):
    def wrap(view_function):
        @wraps(view_function)
        def wrapped_f(*args, **kwargs):
            response = view_function(*args, **kwargs)
            if "export" in request.args:
                asked_format = request.args["export"]
                if asked_format not in export_funcs:
                    return error_400('Export format unknown or unavailable. Available values are : ' + ', '.join(['linkedplaces', 'inline-linkedplaces']))
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




