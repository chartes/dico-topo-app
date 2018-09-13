import os
import sys
import json
from flask_testing import TestCase
from json import JSONDecodeError
from os.path import join
from app import create_app, db


if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads

_app = create_app("test")


class TestBaseServer(TestCase):

    FIXTURES_PATH = join(os.path.dirname(os.path.abspath(__file__)), 'data', 'fixtures')

    BASE_FIXTURES = [

    ]

    def setUp(self):
        with self.app.app_context():
            self.clear_data()
            self.load_sql_fixtures(self.BASE_FIXTURES)

    def create_app(self):
        with _app.app_context():
            db.create_all()
            self.client = _app.test_client(allow_subdomain_redirects=True)
            self.db = db
            self.url_prefix = _app.config["API_URL_PREFIX"]
        return _app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @staticmethod
    def clear_data():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

    def load_sql_fixtures(self, fixtures):
        with self.app.app_context(), db.engine.connect() as connection:
            for fixture in fixtures:
                with open(fixture) as f:
                    for _s in f.readlines():
                        trans = connection.begin()
                        connection.execute(_s, multi=True)
                        trans.commit()

    def get(self, url, **kwargs):
        return self.client.get(url, follow_redirects=True, **kwargs)

    def post(self, url, data, **kwargs):
        return self.client.post(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def put(self, url, data, **kwargs):
        return self.client.put(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def patch(self, url, data, **kwargs):
        return self.client.patch(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def delete(self, url, **kwargs):
        return self.client.delete(url, follow_redirects=True, **kwargs)

    @staticmethod
    def api_query(method, *args, **kwargs):
        r = method(*args, **kwargs)
        if r.data is None:
            return r, r.status, None
        else:
            try:
                data = json_loads(r.data)
            except JSONDecodeError as e:
                data = r.data
            return r, r.status, data

    def api_get(self, *args, **kwargs):
        return TestBaseServer.api_query(self.get, *args, **kwargs)

    def api_post(self, *args, **kwargs):
        return TestBaseServer.api_query(self.post, *args, **kwargs)

    def api_put(self, *args, **kwargs):
        return TestBaseServer.api_query(self.put, *args, **kwargs)

    def api_patch(self, *args, **kwargs):
        return TestBaseServer.api_query(self.patch, *args, **kwargs)

    def api_delete(self, *args, **kwargs):
        return TestBaseServer.api_query(self.delete, *args, **kwargs)
