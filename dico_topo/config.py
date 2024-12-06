from pathlib import Path
import os
from sqlalchemy_utils import database_exists, create_database

HERE = Path(__file__).parent

def parse_var_env(var_name) -> str | bool | None:
    v = os.environ.get(var_name)
    if v == "True":
        v = True
    elif v == "False":
        v = False
    return v

class Config(object):
    SECRET_KEY = parse_var_env('SECRET_KEY')
    ENV ='production'
    DEBUG = parse_var_env('DEBUG')

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + str( HERE / parse_var_env('DATABASE_URI'))
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ELASTICSEARCH_URL = parse_var_env('ELASTICSEARCH_URL')
    DEFAULT_INDEX_NAME = parse_var_env('DEFAULT_INDEX_NAME')
    INDEX_PREFIX = parse_var_env('INDEX_PREFIX')
    SEARCH_RESULT_PER_PAGE =  parse_var_env('SEARCH_RESULT_PER_PAGE')

    APP_URL_PREFIX = parse_var_env('APP_URL_PREFIX')
    API_URL_PREFIX = parse_var_env('API_URL_PREFIX')
    API_VERSION = parse_var_env('API_VERSION')

    @staticmethod
    def init_app(app):
        pass

class StagingConfig(Config):

    ENV = 'development'
    DEBUG = parse_var_env('DEBUG')

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN PRE-PROD MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')
        with app.app_context():
            db_url = app.config["SQLALCHEMY_DATABASE_URI"]
            if not database_exists(db_url):
                create_database(db_url)
            else:
                pass

class LocalConfig(Config):
    ENV = 'development'
    DEBUG = parse_var_env('DEBUG')

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN LOCAL DEV MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')

class TestConfig(Config):
    ENV = 'testing'

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN TEST MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')
        with app.app_context():
            db_url = app.config["SQLALCHEMY_DATABASE_URI"]
            if not database_exists(db_url):
                create_database(db_url)
            else:
                pass

config = {
    "local": LocalConfig,
    "staging": StagingConfig,
    "prod": Config,
    "test": TestConfig
}
