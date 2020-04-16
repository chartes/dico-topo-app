import pprint

from app.api.place.facade import PlaceFacade
from app.models import Place
from tests.base_server import TestBaseServer
from tests.data.fixtures.place import load_fixtures


class TestSortPlace(TestBaseServer):

    def setUp(self):
        super().setUp()

    def test_recursion(self):
        p = PlaceFacade(self.url_prefix, Place.query.first())
        print(p.resource)

    def test_sort_place(self):

        term = "Villema*"
        query = "label.folded:{term}".format(term=term)
        sort = "label.folded"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)
        print(r, status)

        pprint.pprint(
            [
                (r['attributes']['place-label'], r['type'], r['id'])
                for r in res['data']
            ]
        )

