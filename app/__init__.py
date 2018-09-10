from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from config import config


# Initialize Flask extensions
db = SQLAlchemy()

api_bp = Blueprint('api_bp', __name__, template_folder='templates')
app_bp = Blueprint('app_bp', __name__, template_folder='templates', static_folder='static')


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
        app.config.from_object(config)
    else:
        app.config.from_object(config[config_name])

    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config["APP_URL_PREFIX"])

    db.init_app(app)
    config[config_name].init_app(app)

    """
    ========================================================
        Import models
    ========================================================
    """

    from app import routes
    from app import models

    if app.config["DB_DROP_AND_CREATE_ALL"]:
        with app.app_context():
            db.drop_all()
            db.create_all()

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    return app
