
import os
from sqlalchemy_utils import database_exists, create_database

basedir = os.path.abspath(os.path.dirname(__file__))


def parse_var_env(var_name):
    v = os.environ.get(var_name)
    if v == "True":
        v = True
    elif v == "False":
        v = False
    return v


class Config(object):
    SECRET_KEY = parse_var_env('SECRET_KEY')
    ENV ='production'
    DEBUG = parse_var_env('DEBUG') or False

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, parse_var_env('DATABASE_URI'))
    SQLALCHEMY_TRACK_MODIFICATIONS = parse_var_env('SQLALCHEMY_TRACK_MODIFICATIONS') or False
    SQLALCHEMY_ECHO = parse_var_env('SQLALCHEMY_ECHO') or False
    SQLALCHEMY_RECORD_QUERIES = parse_var_env('SQLALCHEMY_RECORD_QUERIES') or False

    DB_DROP_AND_CREATE_ALL = parse_var_env('DB_DROP_AND_CREATE_ALL') or False
    GENERATE_FAKE_DATA = parse_var_env('GENERATE_FAKE_DATA') or False

    ELASTICSEARCH_URL = parse_var_env('ELASTICSEARCH_URL')
    DEFAULT_INDEX_NAME = parse_var_env('DEFAULT_INDEX_NAME')
    INDEX_PREFIX = parse_var_env('INDEX_PREFIX')
    SEARCH_RESULT_PER_PAGE =  parse_var_env('SEARCH_RESULT_PER_PAGE')

    ASSETS_DEBUG = parse_var_env('ASSETS_DEBUG') or False
    SCSS_STATIC_DIR = os.path.join(basedir, "app ", "static", "css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app", "assets", "scss")
    CSRF_ENABLED = parse_var_env('CSRF_ENABLED')

    #APP_URL_PREFIX = parse_var_env('APP_URL_PREFIX')
    #APP_FRONTEND_URL = parse_var_env('APP_FRONTEND_URL')

    API_VERSION = parse_var_env('API_VERSION')
    API_URL_PREFIX = parse_var_env('API_URL_PREFIX')

    # Flask-User settings
    USER_APP_NAME = parse_var_env("USER_APP_NAME") or "Dicotopo"     # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True       # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form
    # Place the Login form and the Register form on one page:
    #USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    #USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'

    USER_ENABLE_REGISTER = parse_var_env('USER_ENABLE_REGISTER')
    USER_ENABLE_REMEMBER_ME = parse_var_env('USER_ENABLE_REMEMBER_ME')
    USER_ENABLE_INVITE_USER = parse_var_env('USER_ENABLE_INVITE_USER')
    USER_REQUIRE_INVITATION = parse_var_env('USER_REQUIRE_INVITATION')
    USER_AUTO_LOGIN_AFTER_CONFIRM = True
    USER_AFTER_LOGOUT_ENDPOINT = 'app_bp.index'
    USER_AFTER_INVITE_ENDPOINT = 'app_bp.after_invite'
    USER_AFTER_REGISTER_ENDPOINT = 'app_bp.index'

    # Flask-Mail settings
    MAIL_USERNAME = parse_var_env('MAIL_USERNAME')
    MAIL_PASSWORD = parse_var_env('MAIL_PASSWORD')
    USER_EMAIL_SENDER_NAME = parse_var_env('USER_EMAIL_SENDER_NAME')
    USER_EMAIL_SENDER_EMAIL = parse_var_env('USER_EMAIL_SENDER_EMAIL')
    MAIL_SERVER = parse_var_env('MAIL_SERVER')
    MAIL_PORT = int(parse_var_env('MAIL_PORT'))
    MAIL_USE_SSL = int(parse_var_env('MAIL_USE_SSL'))
    MAIL_USE_TLS = int(parse_var_env('MAIL_USE_SSL'))
    MAIL_DEBUG = parse_var_env('MAIL_DEBUG')

    JWT_SECRET_KEY = parse_var_env('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_ACCESS_COOKIE_PATH = parse_var_env('JWT_ACCESS_COOKIE_PATH')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    ENV = 'development'

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN DEV MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')
        with app.app_context():
            db_url = app.config["SQLALCHEMY_DATABASE_URI"]
            if not database_exists(db_url):
                create_database(db_url)
            else:
                pass


class TestConfig(Config):
    ENV = 'testing'

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN TEST MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')

config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
