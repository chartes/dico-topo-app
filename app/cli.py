import click

from app import create_app, db, models

app = None


def make_cli():
    """ Creates a Command Line Interface for everydays tasks

    :return: Click groum
    """
    @click.group()
    @click.option('--config', default="dev")
    def cli(config):
        """ Generates the client"""
        click.echo("Loading the application")
        global app
        app = create_app(config)

    @click.command("db-create")
    def db_create():
        """ Creates a local database
        """
        with app.app_context():
            db.create_all()

            db.session.commit()
            click.echo("Created the database")

    @click.command("db-recreate")
    def db_recreate():
        """ Recreates a local database. You probably should not use this on
        production.
        """
        with app.app_context():
            db.drop_all()
            db.create_all()

            db.session.commit()
            click.echo("Dropped then recreated the database")

    @click.command("reindex")
    def db_reindex():
        """
        Rebuild the elasticsearch indexes from the current database
        """
        print("================================")
        print("REINDEXING.... please be patient")
        print("================================")
        with app.app_context():
            #models.FeatureType, models.InseeRef, models.PlacenameAltLabel,
            for m in (models.Placename, models.InseeCommune, models.PlacenameOldLabel):
                print('...%s' % m.__tablename__)
                #app.elasticsearch.indices.delete(index=m.__tablename__, ignore=[404])
                m.reindex()

    @click.command("run")
    def run():
        """ Run the application in Debug Mode [Not Recommended on production]
        """
        app.run()

    cli.add_command(db_create)
    cli.add_command(db_recreate)
    cli.add_command(db_reindex)
    cli.add_command(run)

    return cli
