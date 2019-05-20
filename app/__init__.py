from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from flask import Flask, Blueprint, url_for
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager
from sqlalchemy import event
from sqlalchemy.engine import Engine

from werkzeug.security import generate_password_hash, check_password_hash

from app.api.response_factory import JSONAPIResponseFactory


# Initialize Flask extensions
db = SQLAlchemy()

api_bp = Blueprint('api_bp', __name__)
app_bp = Blueprint('app_bp', __name__, template_folder='templates', static_folder='static')


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)


def create_app(config_name="dev"):
    """ Create the application """
    app = Flask(__name__)
    if not isinstance(config_name, str):
        from config import config
        app.config.from_object(config)
    else:
        print("Load environment variables for config '%s'" % config_name)
        # It is important to load the .env file before parsing the config file
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        env_filename = os.path.join(dir_path, '..', '%s.env' % config_name)
        print(env_filename)
        load_dotenv(env_filename, verbose=True)
        from config import config
        app.config.from_object(config[config_name])

    #app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config["APP_URL_PREFIX"])

    db.init_app(app)
    config[config_name].init_app(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    from app.models import User
    from app.models import UserInvitation

    """
    ========================================================
        Setup Flask-User
    ========================================================
    """

    class CustomUserManager(UserManager):
        def customize(self, app):
            self.UserInvitationClass = UserInvitation
            self.email_manager._render_and_send_email_with_exceptions = self.email_manager._render_and_send_email

            def with_protection(*args, **kargs):
                try:
                    self.email_manager._render_and_send_email_with_exceptions(*args, **kargs)
                except Exception as e:
                    print(e)

            self.email_manager._render_and_send_email = with_protection

        def hash_password(self, password):
            return generate_password_hash(password.encode('utf-8'))

        def verify_password(self, password, password_hash):
            return check_password_hash(password_hash, password)

        def _endpoint_url(self, endpoint):
            return url_for(endpoint) if endpoint else url_for('app_bp.index')

    # Initialize Flask-User
    app.user_manager = CustomUserManager(app, db, UserClass=User, UserInvitationClass=UserInvitation)

    # from flask_user import user_logged_in, user_logged_out, user_changed_password, user_changed_username

    """
    ========================================================
        Setup Flask-JWT-Extended
    ========================================================
    """
    app.jwt = JWTManager(app)

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what custom claims
    # should be added to the access token.
    @app.jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return user["roles"]

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what the identity
    # of the access token should be.
    @app.jwt.user_identity_loader
    def user_identity_lookup(user):
        return user["username"]

    # =====================================
    # Import models & app routes
    # =====================================

    from app import models
    from app import routes

    # =====================================
    # register api routes
    # =====================================

    from app.api.route_registrar import JSONAPIRouteRegistrar
    app.api_url_registrar = JSONAPIRouteRegistrar(app.config["API_VERSION"], app.config["API_URL_PREFIX"])

    from app.api import routes
    from app.api.insee_commune.routes import register_insee_commune_api_urls
    from app.api.insee_ref.routes import register_insee_ref_api_urls
    from app.api.placename.routes import register_placename_api_urls
    from app.api.placename_alt_label.routes import register_placename_alt_label_api_urls
    from app.api.placename_old_label.routes import register_placename_old_label_api_urls
    from app.api.feature_type.routes import register_feature_type_api_urls
    from app.api.decorators import export_to

    with app.app_context():
        # generate resources endpoints
        register_placename_api_urls(app)
        register_placename_alt_label_api_urls(app)
        register_placename_old_label_api_urls(app)
        register_insee_commune_api_urls(app)
        register_insee_ref_api_urls(app)
        register_feature_type_api_urls(app)
        # generate search endpoint
        app.api_url_registrar.register_search_route(decorators=[export_to('linkedplaces')])

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    return app
