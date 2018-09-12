
import os
from sqlalchemy_utils import database_exists, create_database

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_DROP_AND_CREATE_ALL = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'dicotopo.sqlite')
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

    DB_DROP_AND_CREATE_ALL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'dicotopo-dev.sqlite')

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
    DB_DROP_AND_CREATE_ALL = False
    DB_PATH = os.path.join(basedir, "tests", "data")
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), DB_PATH, 'dicotopo-test.sqlite')


config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
