import sys
from app import create_app, db
from flask_script import Manager

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand



if __name__ == '__main__':

    config = sys.argv.pop(1)

    app = create_app(config)
    with app.app_context():
        from app import db

        migrate = Migrate(app, db)
        manager = Manager(app)
        manager.add_command('db', MigrateCommand)

    from app.models import *

    manager.run()
