from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from config import config


# Initialize Flask extensions
db = SQLAlchemy()

api_bp = Blueprint('api_bp', __name__, template_folder='templates')
app_bp = Blueprint('app_bp', __name__, template_folder='templates', static_folder='static')


def create_app(config_name="dev"):
    """ Create the application """
    app = Flask(__name__)
    if not isinstance(config_name, str):
        app.config.from_object(config)
    else:
        app.config.from_object(config[config_name])

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

    app_bp.url_prefix = app.config["APP_URL_PREFIX"]
    api_bp.url_prefix = app.config["APP_URL_PREFIX"]

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    return app
