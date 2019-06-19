from math import floor

import click
import json
import requests
import sqlalchemy
from elasticsearch import AuthorizationException
from jsonschema import validate

from app import create_app

from app.api.placename.facade import PlacenameFacade
from app.api.placename_old_label.facade import PlacenameOldLabelFacade
from app.models import UserRole, User, Placename, PlacenameOldLabel

app = None


def add_default_users(db):
    try:
        UserRole.add_default_roles()
        User.add_default_users()
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print(e)


def load_elastic_conf(conf_name, index_name, delete=False):
    url = '/'.join([app.config['ELASTICSEARCH_URL'], index_name])
    res = None
    try:
        if delete:
            res = requests.delete(url)
            with open('elasticsearch/_settings.conf.json', 'r') as _settings:
                settings = json.load(_settings)

                with open('elasticsearch/%s.conf.json' % conf_name, 'r') as f:
                    payload = json.load(f)
                    payload["settings"] = settings
                    print("PUT", url, payload)
                    res = requests.put(url, json=payload)
                    assert str(res.status_code).startswith("20")

    except FileNotFoundError as e:
        print("no conf...", flush=True, end=" ")
    except Exception as e:
        print(res.text, str(e), flush=True, end=" ")
        raise e


def validateJSONSchema(schema, data):
    validate(instance=data, schema=schema)


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
            from app import db
            db.create_all()

            add_default_users(db)

            db.session.commit()
            click.echo("Created the database")

    @click.command("db-recreate")
    def db_recreate():
        """ Recreates a local database. You probably should not use this on
        production.
        """
        with app.app_context():
            from app import db
            db.drop_all()
            db.create_all()

            add_default_users(db)

            db.session.commit()
            click.echo("Dropped then recreated the database")

    @click.command("db-validate")
    @click.option('--between', required=False)
    def db_validate(between):
        SCHEMA_URL = "https://raw.githubusercontent.com/kgeographer/whgazetteer/master/datasets/static/validate/lpf-schema.json"
        getAPIUrl = lambda \
            id: "http://localhost/dico-topo/api/1.0/placenames/{0}?export=linkedplaces&without-relationships".format(id)
        print("Fetching schema from {0}... ".format(SCHEMA_URL), end='', flush=False)
        r = requests.get(SCHEMA_URL)
        print(r.status_code)
        schema = r.json()

        with app.app_context():

            stmt = Placename.query
            if between:
                boundaries = between.split(",")
                if len(boundaries) == 1:
                    lower_bound = boundaries[0]
                    stmt = stmt.filter(Placename.id >= lower_bound)
                else:
                    lower_bound, upper_bound = boundaries
                    bt_op = sqlalchemy.sql.expression.between
                    stmt = stmt.filter(bt_op(Placename.id, lower_bound, upper_bound))

            for placename in stmt.all():
                print("validating '{0}'... ".format(placename.id), end='', flush=False)
                res_url = getAPIUrl(placename.id)
                r = requests.get(res_url)
                data = r.json()
                features = data.get('features', [])
                print("{0} feature(s) detected... ".format(len(features)), end='', flush=False)

                for feature in features:
                    try:
                        validateJSONSchema(schema, feature)
                        print('OK', flush=True)
                    except Exception as e:
                        print(str(e))
                        print(' .... NOT OK', flush=True)

                        exit(1)

    @click.command("db-reindex")
    @click.option('--indexes', default="all")
    @click.option('--host', required=True)
    @click.option('--between', required=False)
    @click.option('--delete', required=False, default=None)
    def db_reindex(indexes, host, between, delete):
        """
        Rebuild the elasticsearch indexes from the current database
        """
        indexes_info = {
            "placenames": {"facade": PlacenameFacade, "model": Placename, "reload-conf": True},
            "old-labels": {"facade": PlacenameOldLabelFacade, "model": PlacenameOldLabel, "reload-conf": False},
        }

        def reindex_from_info(name, info):

            with app.app_context():

                prefix = "{host}{api_prefix}".format(host=host, api_prefix=app.config["API_URL_PREFIX"])
                print("Reindexing %s" % name, end=" ", flush=True)

                index_name = info["facade"].get_index_name()

                url = "/".join([app.config['ELASTICSEARCH_URL'], index_name, '_settings'])

                def reset_readonly():
                    r = requests.put(url, json={"index.blocks.read_only_allow_delete": None})
                    assert (r.status_code == 200)

                try:
                    if info["reload-conf"]:
                        load_elastic_conf(name, index_name, delete=delete is not None)

                    stmt = info["model"].query

                    if between:
                        boundaries = between.split(",")
                        if len(boundaries) == 1:
                            lower_bound = boundaries[0]
                            stmt = stmt.filter(info["model"].id >= lower_bound)
                        else:
                            lower_bound, upper_bound = boundaries
                            bt_op = sqlalchemy.sql.expression.between
                            stmt = stmt.filter(bt_op(info["model"].id, lower_bound, upper_bound))

                    all_objs = stmt.all()
                    count = len(all_objs)
                    ct = 0
                    print("(%s items)" % count, end=" ", flush=True)
                    last_progress = -1
                    for obj in all_objs:
                        # REINDEX
                        f_obj = info["facade"](prefix, obj)
                        try:
                            f_obj.reindex("insert", propagate=False)
                        except AuthorizationException:
                            reset_readonly()
                            f_obj.reindex("insert", propagate=False)
                        # show progression
                        progress = floor(100 * (ct / count))
                        if progress % 5 == 0 and progress != last_progress:
                            print(progress, end="... ", flush=True)
                            last_progress = progress
                        ct += 1
                    print("OK")
                except Exception as e:
                    print("NOT OK!  ", str(e))

        if indexes == "all":  # reindex every index configured above
            indexes = ",".join(indexes_info.keys())

        for name in indexes.split(","):
            if name in indexes_info:
                reindex_from_info(name, indexes_info[name])
            else:
                print("Warning: index %s does not exist or is not declared in the cli" % name)

    @click.command("run")
    def run():
        """ Run the application in Debug Mode [Not Recommended on production]
        """
        app.run()

    cli.add_command(db_create)
    cli.add_command(db_recreate)
    cli.add_command(db_reindex)
    cli.add_command(db_validate)
    cli.add_command(run)

    return cli
