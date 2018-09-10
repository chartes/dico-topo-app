
import os
from sqlalchemy_utils import database_exists, create_database

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_HOST = '127.0.0.1'
    DB_PORT = 3309
    DB_SCHEMA = 'dicotopo'
    DB_USER = 'USE_AN_ENV_VAR'
    DB_PWD = 'USE_AN_ENV_VAR'
    DB_DROP_AND_CREATE_ALL = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DICO_TOPO_DATABASE_URL') or \
        'mysql+pymysql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_SCHEMA)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SCSS_STATIC_DIR = os.path.join(basedir, "app ", "static", "css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app", "assets", "scss")
    CSRF_ENABLED = True

    APP_URL_PREFIX = '/dico-topo'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_ECHO = True

    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_SCHEMA = 'dico-topo-dev'
    DB_USER = ''
    DB_PWD = ''
    DB_DROP_AND_CREATE_ALL = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_SCHEMA
    )

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN DEBUG MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')

        with app.app_context():
            db_url = app.config["SQLALCHEMY_DATABASE_URI"]
            if not database_exists(db_url):
                create_database(db_url)
                print("Database %s has been created" % db_url)
            else:
                print("Database %s already exists" % db_url)


class TestConfig(Config):
    DB_PORT = 3308


config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
