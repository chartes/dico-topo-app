from math import floor

import click
import json
import requests
import sqlalchemy
from elasticsearch import AuthorizationException
from jsonschema import validate
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app import create_app

from app.api.place.facade import PlaceFacade
from app.api.place_old_label.facade import PlaceOldLabelFacade
from app.models import Place, PlaceOldLabel, IdRegister, PlaceAltLabel, PlaceComment, PlaceDescription, PlaceFeatureType

app = None


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
        print(app.config['SQLALCHEMY_DATABASE_URI'])

    @click.command("db-create")
    def db_create():
        """ Creates a local database
        """
        with app.app_context():
            from app import db
            db.create_all()

            db.session.commit()
            click.echo("Created the database")

    @click.command("db-recreate")
    @click.option('--insert', required=False, default=[], help="--insert ../db/fixtures/file1.sql,../db/fixutres/file2/sql")
    @click.option('--unstrict', is_flag=True, help="--unstrict disable foreign keys verification")
    def db_recreate(insert, unstrict):
        """ Recreates a local database. You probably should not use this on
        production.
        """
        with app.app_context():
            from app import db
            db.drop_all()
            db.create_all()
            click.echo("DB has been dropped and recreated")
            db.session.commit()

            if len(insert) > 0:
                with db.engine.connect() as connection:
                    if unstrict:
                        connection.execute("PRAGMA foreign_keys=OFF")
                    for file in insert.split(','):
                        with open(file) as f:
                            click.echo("Insertion of {0}...".format(file))
                            for _s in f.readlines():
                                trans = connection.begin()
                                connection.execute(_s, multi=True)
                                trans.commit()
                click.echo("Insertions done")

    @click.command("db-validate")
    @click.option('--between', required=False)
    def db_validate(between):
        SCHEMA_URL = "https://raw.githubusercontent.com/kgeographer/whgazetteer/master/datasets/static/validate/lpf-schema.json"
        getAPIUrl = lambda \
            id: "http://localhost/dico-topo/api/1.0/places/{0}?export=linkedplaces&without-relationships".format(id)
        print("Fetching schema from {0}... ".format(SCHEMA_URL), end='', flush=False)
        r = requests.get(SCHEMA_URL)
        print(r.status_code)
        schema = r.json()

        with app.app_context():

            stmt = Place.query
            if between:
                boundaries = between.split(",")
                if len(boundaries) == 1:
                    lower_bound = boundaries[0]
                    stmt = stmt.filter(Place.id >= lower_bound)
                else:
                    lower_bound, upper_bound = boundaries
                    bt_op = sqlalchemy.sql.expression.between
                    stmt = stmt.filter(bt_op(Place.id, lower_bound, upper_bound))

            for place in stmt.all():
                print("validating '{0}'... ".format(place.id), end='', flush=False)
                res_url = getAPIUrl(place.id)
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
        print(indexes, host, between, delete)
        indexes_info = {
            "places": {"facade": PlaceFacade, "model": Place, "reload-conf": True},
            "old-labels": {"facade": PlaceOldLabelFacade, "model": PlaceOldLabel, "reload-conf": False},
        }

        def reindex_from_info(name, info):

            with app.app_context():

                prefix = "{host}{api_prefix}".format(host=host, api_prefix=app.config.get("API_URL_PREFIX", ""))
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

    @click.command("id-register")
    @click.option('--clear/--no-clear', required=False, default=False)
    @click.option('--replace/--append', required=False, default=False)
    @click.option('--update-app/--no-update-app', required=False, default=False)
    @click.option('--update-only', required=False, default=False, is_flag=True)
    def id_register(clear, replace, update_app, update_only):
        """
        :param update_only:
        :param update_app:
        :param clear:
        :param replace:
        :return:
        """
        with app.app_context():

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=OFF")
                cursor.close()

            from app import db
            db.create_all()
            try:
                if not update_only:
                    if clear:
                        IdRegister.query.delete()
                        db.session.commit()
                        print('register cleared!')

                    # replace existing ids in the register with new ones
                    if replace:
                        print('replacing places found in the register and adding the new ones...')
                        for place in Place.query.all():
                            elt = IdRegister.query.filter(IdRegister.secondary_value == place.id).first()
                            if elt:
                                elt.secondary_value = place.id
                                db.session.flush()
                    else:
                        print('registering places not found in the register...')
                        for place in Place.query.all():
                            # append only new ids to the register
                            if not db.session.query(
                                    IdRegister.query.filter(IdRegister.secondary_value == place.id).exists()
                            ).scalar():
                                elt = IdRegister(place.id)
                                db.session.add(elt)
                                db.session.flush()

                if update_app or update_only:
                    # update the whole application using the ids stored in the register
                    for elt in IdRegister.query.filter(IdRegister.secondary_value is not None).all():
                        new_id, old_id = elt.primary_value, elt.secondary_value

                        with db.session.no_autoflush:

                            p = Place.query.filter(Place.id == old_id).first()
                            if p:
                                p.id = new_id

                                for p_alt in PlaceAltLabel.query.filter(PlaceAltLabel.place_id == old_id).all():
                                    p_alt.place_id = new_id

                                for p_old in PlaceOldLabel.query.filter(PlaceOldLabel.place_id == old_id).all():
                                    p_old.place_id = new_id

                                for p_feat in PlaceFeatureType.query.filter(PlaceFeatureType.place_id == old_id).all():
                                    p_feat.place_id = new_id

                                for p_co in PlaceComment.query.filter(PlaceComment.place_id == old_id).all():
                                    p_co.place_id = new_id

                                for p_desc in PlaceDescription.query.filter(PlaceDescription.place_id == old_id).all():
                                    p_desc.place_id = new_id

                            db.session.flush()

                    print('application IDS have been updated!')

                db.session.commit()
            except Exception as e:
                print(str(e))
                db.session.rollback()


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
    cli.add_command(id_register)

    return cli
