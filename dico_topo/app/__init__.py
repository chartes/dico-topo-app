from sys import prefix
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from flask import Flask, Blueprint
#from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


from dico_topo.app.api.response_factory import JSONAPIResponseFactory

HERE = Path(__file__).parent

# Initialize Flask extensions
db = SQLAlchemy()

api_bp = Blueprint('api_bp', __name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_app(config_name="staging"):
    """ Create the application """
    app = Flask(__name__)
    if not isinstance(config_name, str):
        from dico_topo.config import config
        app.config.from_object(config)
    else:
        print("Load environment variables for config '%s'" % config_name)
        # It is important to load the .env file before parsing the config file
        project_path = HERE.parent.parent
        env_filename = project_path / ('%s.env' % config_name)
        print(".env file to be loaded : ", env_filename)
        load_dotenv(env_filename, verbose=True)
        from dico_topo.config import config
        app.config.from_object(config[config_name])

    db.init_app(app)
    config[config_name].init_app(app)
    #migrate = Migrate(app, db)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    # =====================================
    # Import models & app routes
    # =====================================

    from dico_topo.app import models
    from dico_topo.app import routes

    # =====================================
    # register api routes
    # =====================================

    from dico_topo.app.api.route_registrar import JSONAPIRouteRegistrar
    app.api_url_registrar = JSONAPIRouteRegistrar(app.config["API_VERSION"], app.config["API_URL_PREFIX"])

    from dico_topo.app.api import routes
    from dico_topo.app.api.insee_commune.routes import register_insee_commune_api_urls
    from dico_topo.app.api.insee_ref.routes import register_insee_ref_api_urls
    from dico_topo.app.api.place.routes import register_place_api_urls
    from dico_topo.app.api.place_description.routes import register_place_description_api_urls
    from dico_topo.app.api.place_comment.routes import register_place_comment_api_urls
    from dico_topo.app.api.place_old_label.routes import register_place_old_label_api_urls
    from dico_topo.app.api.place_feature_type.routes import register_feature_type_api_urls
    from dico_topo.app.api.bibl.routes import register_bibl_api_urls
    from dico_topo.app.api.responsibility.routes import register_responsibility_api_urls
    from dico_topo.app.api.user.routes import register_user_api_urls

    from dico_topo.app.api.decorators import export_to

    with app.app_context():
        # generate resources endpoints
        register_place_api_urls(app)
        register_place_description_api_urls(app)
        register_place_comment_api_urls(app)
        register_place_old_label_api_urls(app)
        register_insee_commune_api_urls(app)
        register_insee_ref_api_urls(app)
        register_feature_type_api_urls(app)
        register_bibl_api_urls(app)
        register_responsibility_api_urls(app)
        register_user_api_urls(app)

        # generate search endpoint
        app.api_url_registrar.register_search_route(decorators=[export_to('linkedplaces')])

        app.register_blueprint(api_bp, url_prefix=app.config["API_URL_PREFIX"])

    return app
