import pprint

from app.api.place.facade import PlaceFacade
from app.models import Place, User, Bibl, RespStatement, PlaceCitableElement, CitableElement
from tests.base_server import TestBaseServer
from tests.data.fixtures.place import load_fixtures


class TestSortPlace(TestBaseServer):

    def setUp(self):
        super().setUp()
        self.db.drop_all()
        self.db.create_all()

    #def test_recursion(self):
    #    p = PlaceFacade(self.url_prefix, Place.query.first())
    #    print(p.resource)
    #    print(self.app.config['SQLALCHEMY_DATABASE_URI'])

    def test_data_creation(self):
        # test du sort en mode 'Toponymes', colonne 'toponyme'
        self.assertTrue(True)

        u1 = User(username="Conservator57")
        u2 = User(username="Analyst99")

        b = Bibl(abbr="abbr", bibl="DT de test")
        r1 = RespStatement(user=u1, bibl=b, resp="Conservator")
        r2 = RespStatement(user=u2,  resp="Analyst")

        p = Place(id="DT99-0001", country="fr", dpt="99", label="Laon")

        # mention de responsabilité r1
        data = [("description", "desc1"), ("comment", "comment1")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r1))

        self.db.session.add(p)
        self.db.session.commit()

        for citable in p.citable_elements:
            print(citable.key, citable.value, citable.resp_stmt)

        # mention de responsabilité r2
        data = [("description", "desc2"), ("comment", "comment2")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r2))

        self.db.session.commit()
        print('='*80)
        for citable in p.citable_elements:
            print(citable.key, citable.value, citable.resp_stmt)
