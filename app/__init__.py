from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from werkzeug.contrib.profiler import ProfilerMiddleware

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
        load_dotenv('%s.env' % config_name, verbose=True)
        from config import config
        app.config.from_object(config[config_name])

    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config["APP_URL_PREFIX"])

    db.init_app(app)
    config[config_name].init_app(app)

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
    from app.api.placename.routes import register_placename_api_urls
    from app.api.placename_alt_label.routes import register_placename_alt_label_api_urls
    from app.api.placename_old_label.routes import register_placename_old_label_api_urls
    from app.api.feature_type.routes import register_feature_type_api_urls

    with app.app_context():
        # generate resources endpoints
        register_placename_api_urls(app)
        register_placename_alt_label_api_urls(app)
        register_placename_old_label_api_urls(app)
        register_insee_commune_api_urls(app)
        register_insee_ref_api_urls(app)
        register_feature_type_api_urls(app)
        # generate search endpoint
        app.api_url_registrar.register_search_route()

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    if app.config["DB_DROP_AND_CREATE_ALL"]:
        print("DB_DROP_AND_CREATE_ALL")
        with app.app_context():
            db.drop_all()
            db.create_all()

    if "REINDEX" in app.config and app.config["REINDEX"] is True:
        print("================================")
        print("REINDEXING.... please be patient")
        print("================================")
        with app.app_context():
            #models.FeatureType, models.InseeRef, models.PlacenameAltLabel,
            for m in (models.Placename, models.InseeCommune, models.PlacenameOldLabel):
                print('...%s' % m.__tablename__)
                #app.elasticsearch.indices.delete(index=m.__tablename__, ignore=[404])
                m.reindex()

    return app
