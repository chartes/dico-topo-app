from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from flask import Flask, Blueprint, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
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
    migrate = Migrate(app, db)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

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
    from app.api.place.routes import register_place_api_urls
    from app.api.place_alt_label.routes import register_place_alt_label_api_urls
    from app.api.place_old_label.routes import register_place_old_label_api_urls
    from app.api.feature_type.routes import register_feature_type_api_urls
    from app.api.bibl.routes import register_bibl_api_urls
    from app.api.decorators import export_to

    with app.app_context():
        # generate resources endpoints
        register_place_api_urls(app)
        register_place_alt_label_api_urls(app)
        register_place_old_label_api_urls(app)
        register_insee_commune_api_urls(app)
        register_insee_ref_api_urls(app)
        register_feature_type_api_urls(app)
        register_bibl_api_urls(app)
        # generate search endpoint
        app.api_url_registrar.register_search_route(decorators=[export_to('linkedplaces')])

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    return app
