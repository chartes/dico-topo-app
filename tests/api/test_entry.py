from tests.api.insee_commune import TestInseeCommune
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
                         ["orth", "country", "dpt", "def", "localization-certainty"])
        self.assertEqual("Commune Un", entry["attributes"]["orth"])
        self.assertEqual("FR", entry["attributes"]["country"])
        self.assertEqual("57", entry["attributes"]["dpt"])
        self.assertEqual("low", entry["attributes"]["localization-certainty"])

        # test the relationships
        self.assertEqual(list(entry['relationships'].keys()),
                         ["insee-commune", "localization-insee-commune",
                          "localization-entry", "alt-orths", "old-orths"])
        for rel in entry['relationships'].values():
            self.assertEqual(list(rel.keys()), ["links", "data"])
            self.assertEqual(list(rel["links"].keys()), ["self", "related"])

        # test the meta data
        # TODO
        # test the top level links
        # TODO
        # test wrong ids
        # TODO
        r, status, obj = self.api_get('%s/entries/9999' % self.url_prefix)
        self.assert404(r)

    def test_get_entry_insee_commune(self):
        r, status, obj = self.api_get('%s/entries/id1' % self.url_prefix)
        self.assertIn('data', obj)
        entry = obj["data"]

        # insee-commune
        # ============= 
        rel = entry['relationships']["insee-commune"]
        # ------ test the relationship link
        self.assertEqual("%s/entries/id1/relationships/insee-commune" % self.url_prefix, rel["links"]["self"])
        r, status, links_self = self.api_get(rel["links"]["self"])
        self.assertEqual({
                "links": rel["links"],
                "data": rel["data"]
            },
            links_self)
        self.assertEqual({"type": "insee-commune", "id": "Commune1"}, rel["data"])
        # ------ test the related resource link
        self.assertEqual("%s/entries/id1/insee-commune" % self.url_prefix, rel["links"]["related"])
        r, status, related_commune = self.api_get(rel["links"]["related"])
        self.assertEqual(rel["data"]["type"], related_commune["data"]["type"])
        self.assertEqual(rel["data"]["id"], related_commune["data"]["id"])

        # test the relationships pagination links if any
        # TODO
        # test when the relationships is empty
        # TODO
        # test wrong ids
        # TODO

