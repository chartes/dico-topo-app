from flask import jsonify, current_app, request
from flask_jwt_extended import create_access_token, set_access_cookies, \
    unset_jwt_cookies
from flask_login import current_user

from app import api_bp
from app.models import User


@api_bp.route('/api/<api_version>/token/auth', methods=['POST'])
def create_token(api_version):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter(User.username == username).first()
    from app.api.decorators import error_401

    if user is None:
        return error_401
    else:
        passwords_match = current_app.user_manager.verify_password(password, user.password)
        if not passwords_match:
            return error_401

    access_token = create_access_token(identity=user.to_json())
    ret = {'access_token': access_token}
    return jsonify(ret), 200


@api_bp.route('/api/<api_version>/token/refresh')
def index(api_version):
    user = current_user
    if not user.is_anonymous:
        access_token = create_access_token(identity=user.to_json(), fresh=True)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        print("set cookies", user)
    else:
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        print("unset cookies")

    return resp, 200


from .capabilities import *