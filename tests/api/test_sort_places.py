import pprint

from app.api.place.facade import PlaceFacade
from app.models import Place
from tests.base_server import TestBaseServer
from tests.data.fixtures.place import load_fixtures


class TestSortPlace(TestBaseServer):

    def setUp(self):
        super().setUp()

    #def test_recursion(self):
    #    p = PlaceFacade(self.url_prefix, Place.query.first())
    #    print(p.resource)
    #    print(self.app.config['SQLALCHEMY_DATABASE_URI'])

    def test_sort_toponym_toponym(self):
        # test du sort en mode 'Toponymes', colonne 'toponyme'
        term = "test_*"
        query = "label.folded:{term}".format(term=term)
        sort = "label.keyword"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['place-label'], r['type'], r['id'])
            for r in res['data']
        ]
        expected = [
            ('test_Aaaallancourt', 'place', 'DT10-00001'),
            ("test_Aaaallancourt (L')", 'place', 'DT10-00048'),
            ("test_Aaabllancourt (L'étang)", 'place', 'DT10-00049'),
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34059),
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34060),
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34061),
            ('Ailleville', 'place-old-label', 34079),
            ('Coeur', 'place-old-label', 34078)
        ]

        self.assertListEqual(expected, actual)

    def test_sort_toponym_place(self):
        term = "test_*"
        query = "label.folded:{term}".format(term=term)
        sort = "place-label.keyword"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['place-label'], r['type'], r['id'])
            for r in res['data']
        ]
        expected = [
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34061),
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34060),
            ("Abbaye-sous-Plancy (L')", 'place-old-label', 34059),
            ('Ailleville', 'place-old-label', 34079),
            ('Coeur', 'place-old-label', 34078),
            ('test_Aaaallancourt', 'place', 'DT10-00001'),
            ("test_Aaaallancourt (L')", 'place', 'DT10-00048'),
            ("test_Aaabllancourt (L'étang)", 'place', 'DT10-00049'),
        ]

        self.assertListEqual(expected, actual)

    def test_sort_toponym_commune(self):
        term = "test_*"
        query = "label.folded:{term}".format(term=term)
        sort = "commune-label.keyword"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['commune-label'], r['type'], r['id'])
            for r in res['data']
        ]

        pprint.pprint(actual)
        pprint.pprint(res['data'])
        expected = [('Ailleville', 'place-old-label', 34079),
                    ('Argançon', 'place', 'DT10-00049'),
                    ('Arrentières', 'place', 'DT10-00048'),
                    ("Plancy-l'Abbaye", 'place-old-label', 34061),
                    ("Plancy-l'Abbaye", 'place-old-label', 34060),
                    ("Plancy-l'Abbaye", 'place-old-label', 34059),
                    ('Villenauxe-la-Grande', 'place', 'DT10-00001'),
                    (None, 'place-old-label', 34078)]

        self.assertListEqual(expected, actual)

