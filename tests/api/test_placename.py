from app.api.place.facade import PlaceFacade
from app.models import Place
from tests.base_server import TestBaseServer
from tests.data.fixtures.place import load_fixtures


class TestPlace(TestBaseServer):

    def setUp(self):
        super().setUp()
        load_fixtures(self.db)
        self.url_prefix = "http://localhost" + self.app.config["API_URL_PREFIX"]

    def test_recursion(self):
        p = PlaceFacade(self.url_prefix, Place.query.first())
        print(p.resource)

    def test_get_place(self):
        r, status, obj = self.api_get('%s/places/id1' % self.url_prefix)
        self.assertIn('data', obj)
        place = obj["data"]

        # test the resource identifier
        self.assertEqual(place['type'], 'place')
        self.assertEqual(place['id'], 'id1')

        # test the attributes
        self.assertEqual(list(place['attributes'].keys()),
                         ["label", "country", "dpt", "desc", "num-start-page",
                          "localization-certainty", "localization-insee-code", "comment"])
        self.assertEqual("Commune Un", place["attributes"]["label"])
        self.assertEqual("FR", place["attributes"]["country"])
        self.assertEqual("57", place["attributes"]["dpt"])
        self.assertEqual("low", place["attributes"]["localization-certainty"])
        self.assertEqual(1, place["attributes"]["num-start-page"])
        self.assertEqual("this is a comment", place["attributes"]["comment"])

        # test the presence of the required relationships
        self.assertEqual(["commune", "localization-commune",
                          "linked-places", "alt-labels", "old-labels"], list(place['relationships'].keys()))
        for rel in place['relationships'].values():
            self.assertEqual(["links", "data"], list(rel.keys()))
            self.assertEqual(["self", "related"], list(rel["links"].keys()))

        # test pagination links
        #self._test_pagination_links(place)
        # test the meta data
        self.assertEqual(place['meta'], {})
        # test the top level links
        self.assertEqual('%s/places/id1' % self.url_prefix, place["links"]["self"])
        # test wrong ids
        r, status, obj = self.api_get('%s/places/9999' % self.url_prefix)
        self.assert404(r)

    def test_get_place_commune(self):
        r, status, obj = self.api_get('%s/places/id1' % self.url_prefix)
        self.assertIn('data', obj)
        rel = obj["data"]['relationships']["commune"]

        # ======= test the relationship link
        self.assertEqual("%s/places/id1/relationships/commune" % self.url_prefix, rel["links"]["self"])
        r, status, links_self = self.api_get(rel["links"]["self"])
        self.assertEqual({"type": "commune", "id": "Commune1"}, rel["data"])
        # test wrong ids
        r, status, obj = self.api_get('%s/places/9999/relationships/commune' % self.url_prefix)
        self.assert404(r)

        # ======= test the related resource link
        self.assertEqual("%s/places/id1/commune" % self.url_prefix, rel["links"]["related"])
        r, status, related_commune = self.api_get(rel["links"]["related"])
        # do not test more than the resource identifier in this test
        self.assertEqual(rel["data"]["type"], related_commune["data"]["type"])
        self.assertEqual(rel["data"]["id"], related_commune["data"]["id"])
        # test wrong ids
        r, status, obj = self.api_get('%s/places/9999/commune' % self.url_prefix)
        self.assert404(r)

        # test the relationships pagination links if any
        #self._test_pagination_links(rel)
        # test when the relationship is empty
        r, status, obj = self.api_get('%s/places/id3/relationships/commune' % self.url_prefix)
        self.assertEqual(None, obj["data"])


