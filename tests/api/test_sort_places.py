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


    def test_sort_toponym_commune_with_dpt_filter(self):
        pass

    def test_sort_toponym_bourg(self):
        # test du sort en mode 'Toponymes', colonne 'toponyme'
        term = "bourg"
        query = "label.folded:{term}".format(term=term)
        sort = "label.keyword"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['place-label'], r['type'], r['id'])
            for r in res['data']
        ]
        expected =  [
            ('Bourg', 'place', 'DT10-00432'),
            ('Bourg (en Bresse)', 'place', 'DT10-00435'),
            ('bourg en bresse', 'place', 'DT10-00430'),
            ('bourg en bresse', 'place', 'DT10-00437'),
            ('Bourg en Bresse', 'place', 'DT10-00433'),
            ('Bourg-en-Bresse', 'place', 'DT10-00431'),
            ("Bourg-l'Évêque (Le)", 'place', 'DT10-00424'),
            ('Bourg-Neuf (Le)', 'place', 'DT10-00425'),
            ('Bourg-Partie (Le)', 'place', 'DT10-00426'),
            ('Bourg-Partie (Le)', 'place-old-label', 35142),
            ('Bresse en Bourg', 'place', 'DT10-00436'),
            ('Brienne-le-Château', 'place-old-label', 35333),
            ('Saint-Jacques', 'place-old-label', 40851),
            ('Villiers', 'place-old-label', 42811),
            ('Villiers-le-Bourg', 'place-old-label', 42457),
            ('Villiers-le-Bourg', 'place', 'DT10-03461')
        ]

        self.assertListEqual(expected, actual)

    def test_sort_toponym_bourg_and_filter_dpt(self):
        # test du sort en mode 'Toponymes', colonne 'toponyme'
        term = "bourg"
        query = "label.folded:{term}".format(term=term)
        sort = "label.keyword"
        url = "/search?query={query}&sort={sort}".format(query=query, sort=sort)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['place-label'], r['type'], r['id'])
            for r in res['data']
        ]
        expected = [
            ('Bourg', 'place', 'DT10-00432'),
            ('Bourg (en Bresse)', 'place', 'DT10-00435'),
            ('bourg en bresse', 'place', 'DT10-00430'),
            ('bourg en bresse', 'place', 'DT10-00437'),
            ('Bourg en Bresse', 'place', 'DT10-00433'),
            ('Bourg-en-Bresse', 'place', 'DT10-00431'),
            ("Bourg-l'Évêque (Le)", 'place', 'DT10-00424'),
            ('Bourg-Neuf (Le)', 'place', 'DT10-00425'),
            ('Bourg-Partie (Le)', 'place', 'DT10-00426'),
            ('Bourg-Partie (Le)', 'place-old-label', 35142),
            ('Bresse en Bourg', 'place', 'DT10-00436'),
            ('Brienne-le-Château', 'place-old-label', 35333),
            ('Saint-Jacques', 'place-old-label', 40851),
            ('Villiers', 'place-old-label', 42811),
            ('Villiers-le-Bourg', 'place-old-label', 42457),
            ('Villiers-le-Bourg', 'place', 'DT10-03461')
        ]

        self.assertListEqual(expected, actual)

    def test_sort_multi_criteriae_with_filter(self):
        # test du sort en mode 'Toponymes', colonne 'toponyme'
        term = "babelin"
        query = "label.folded:{term}".format(term=term)
        filter = " AND (dep-id:34 OR dep-id:10)"
        sort = "-place-label.keyword,dep-id.keyword"
        groupby="groupby[doc-type]=place&groupby[field]=place-id.keyword"
        url = "/search?query={query}&sort={sort}&{groupby}".format(query=query+filter, sort=sort, groupby=groupby)

        r, status, res = self.api_get(url)

        actual = [
            (r['attributes']['place-label'], r['type'], r['id'])
            for r in res['data']
        ]

        pprint.pprint(actual)

        expected = [('Babelin les trois quarts', 'place', 'DT10-00106'),  # dpt 10
                    ("Babelin (l'église)", 'place', 'DT10-00111'),        # dpt 10
                    ('Babelin plage', 'place', 'DT10-00124'),             # dpt 34
                    ('babelin la moulasse', 'place', 'DT10-00125'),       # dpt 34
                    ('Babelin saint loup', 'place', 'DT10-00123')]        # dpt 34


        self.assertListEqual(expected, actual)

