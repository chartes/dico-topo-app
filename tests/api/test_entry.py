from tests.base_server import TestBaseServer
from tests.data.fixtures.entry import load_fixtures


class TestEntry(TestBaseServer):

    def setUp(self):
        super().setUp()
        load_fixtures(self.db)
        self.url_prefix = self.app.config["API_URL_PREFIX"]

    def test_get_entry(self):
        r, status, obj = self.api_get('%s/entries/id1' % self.url_prefix)
        self.assertIn('data', obj)
        entry = obj["data"]

        # test the resource identifier
        self.assertEqual(entry['type'], 'entry')
        self.assertEqual(entry['id'], 'id1')

        # test the attributes
        self.assertEqual(list(entry['attributes'].keys()),
                         ["orth", "country", "dpt", "def", "start-page", "localization-certainty"])
        self.assertEqual("Commune Un", entry["attributes"]["orth"])
        self.assertEqual("FR", entry["attributes"]["country"])
        self.assertEqual("57", entry["attributes"]["dpt"])
        self.assertEqual("low", entry["attributes"]["localization-certainty"])
        self.assertEqual(1, entry["attributes"]["start-page"])

        # test the presence of the required relationships
        self.assertEqual(["commune", "linked-commune",
                          "linked-placenames", "alt-orths", "old-orths"], list(entry['relationships'].keys()))
        for rel in entry['relationships'].values():
            self.assertEqual(["links", "data"], list(rel.keys()))
            self.assertEqual(["self", "related"], list(rel["links"].keys()))

        # test pagination links
        #self._test_pagination_links(entry)
        # test the meta data
        self.assertEqual(entry['meta'], {})
        # test the top level links
        self.assertEqual('%s/entries/id1' % self.url_prefix, entry["links"]["self"])
        # test wrong ids
        r, status, obj = self.api_get('%s/entries/9999' % self.url_prefix)
        self.assert404(r)

    def test_get_entry_commune(self):
        r, status, obj = self.api_get('%s/entries/id1' % self.url_prefix)
        self.assertIn('data', obj)
        rel = obj["data"]['relationships']["commune"]

        # ======= test the relationship link
        self.assertEqual("%s/entries/id1/relationships/commune" % self.url_prefix, rel["links"]["self"])
        r, status, links_self = self.api_get(rel["links"]["self"])
        self.assertEqual({"links": rel["links"], "data": rel["data"]}, links_self)
        self.assertEqual({"type": "commune", "id": "Commune1"}, rel["data"])
        # test wrong ids
        r, status, obj = self.api_get('%s/entries/9999/relationships/commune' % self.url_prefix)
        self.assert404(r)

        # ======= test the related resource link
        self.assertEqual("%s/entries/id1/commune" % self.url_prefix, rel["links"]["related"])
        r, status, related_commune = self.api_get(rel["links"]["related"])
        # do not test more than the resource identifier in this test
        print(rel["data"]["type"], related_commune["data"]["type"])
        self.assertEqual(rel["data"]["type"], related_commune["data"]["type"])
        self.assertEqual(rel["data"]["id"], related_commune["data"]["id"])
        # test wrong ids
        r, status, obj = self.api_get('%s/entries/9999/commune' % self.url_prefix)
        self.assert404(r)

        # test the relationships pagination links if any
        #self._test_pagination_links(rel)
        # test when the relationship is empty
        r, status, obj = self.api_get('%s/entries/id3/relationships/commune' % self.url_prefix)
        self.assertEqual(None, obj["data"])


