
from tests.base_server import TestBaseServer, json_loads


class TestEntry(TestBaseServer):

    FIXTURES = [
    ]

    def test_get_entry(self):
        self.assertEquals(1, 2)
