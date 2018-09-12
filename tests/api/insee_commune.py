
from tests.base_server import TestBaseServer
from tests.data.fixtures.insee_commune import load_fixtures


class TestInseeCommune(TestBaseServer):

    def setUp(self):
        super().setUp()
        load_fixtures(self.db)

    def test_insee_commune(self):
        r, status, obj = self.api_get('%s/insee-communes/Commune1' % self.url_prefix)
        self.assertIn('data', obj)
        raise NotImplementedError
