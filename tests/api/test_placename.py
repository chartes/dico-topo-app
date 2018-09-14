from tests.base_server import TestBaseServer
from tests.data.fixtures.placename import load_fixtures


class TestPlacename(TestBaseServer):

    def setUp(self):
        super().setUp()
        load_fixtures(self.db)
        self.url_prefix = self.app.config["API_URL_PREFIX"]

    def test_get_placename(self):
        r, status, obj = self.api_get('%s/placenames/id1' % self.url_prefix)
        self.assertIn('data', obj)
        placename = obj["data"]

        # test the resource identifier
        self.assertEqual(placename['type'], 'placename')
        self.assertEqual(placename['id'], 'id1')

        # test the attributes
        self.assertEqual(list(placename['attributes'].keys()),
                         ["label", "country", "dpt", "desc", "num-start-page", "localization-certainty", "comment"])
        self.assertEqual("Commune Un", placename["attributes"]["label"])
        self.assertEqual("FR", placename["attributes"]["country"])
        self.assertEqual("57", placename["attributes"]["dpt"])
        self.assertEqual("low", placename["attributes"]["localization-certainty"])
        self.assertEqual(1, placename["attributes"]["num-start-page"])
        self.assertEqual("this is a comment", placename["attributes"]["comment"])

        # test the presence of the required relationships
        self.assertEqual(["commune", "linked-commune",
                          "linked-placenames", "alt-labels", "old-labels"], list(placename['relationships'].keys()))
        for rel in placename['relationships'].values():
            self.assertEqual(["links", "data"], list(rel.keys()))
            self.assertEqual(["self", "related"], list(rel["links"].keys()))

        # test pagination links
        #self._test_pagination_links(placename)
        # test the meta data
        self.assertEqual(placename['meta'], {})
        # test the top level links
        self.assertEqual('%s/placenames/id1' % self.url_prefix, placename["links"]["self"])
        # test wrong ids
        r, status, obj = self.api_get('%s/placenames/9999' % self.url_prefix)
        self.assert404(r)

    def test_get_placename_commune(self):
        r, status, obj = self.api_get('%s/placenames/id1' % self.url_prefix)
        self.assertIn('data', obj)
        rel = obj["data"]['relationships']["commune"]

        # ======= test the relationship link
        self.assertEqual("%s/placenames/id1/relationships/commune" % self.url_prefix, rel["links"]["self"])
        r, status, links_self = self.api_get(rel["links"]["self"])
        self.assertEqual({"links": rel["links"], "data": rel["data"]}, links_self)
        self.assertEqual({"type": "commune", "id": "Commune1"}, rel["data"])
        # test wrong ids
        r, status, obj = self.api_get('%s/placenames/9999/relationships/commune' % self.url_prefix)
        self.assert404(r)

        # ======= test the related resource link
        self.assertEqual("%s/placenames/id1/commune" % self.url_prefix, rel["links"]["related"])
        r, status, related_commune = self.api_get(rel["links"]["related"])
        # do not test more than the resource identifier in this test
        self.assertEqual(rel["data"]["type"], related_commune["data"]["type"])
        self.assertEqual(rel["data"]["id"], related_commune["data"]["id"])
        # test wrong ids
        r, status, obj = self.api_get('%s/placenames/9999/commune' % self.url_prefix)
        self.assert404(r)

        # test the relationships pagination links if any
        #self._test_pagination_links(rel)
        # test when the relationship is empty
        r, status, obj = self.api_get('%s/placenames/id3/relationships/commune' % self.url_prefix)
        self.assertEqual(None, obj["data"])


