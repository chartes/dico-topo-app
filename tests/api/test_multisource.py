import pprint

from app.api.place.facade import PlaceFacade
from app.models import Place, User, Bibl, RespStatement, PlaceCitableElement, CitableElement, ReferencedByBibl, \
    PlaceOldLabel
from tests.base_server import TestBaseServer
from tests.data.fixtures.place import load_fixtures


class TestMultisource(TestBaseServer):

    def setUp(self):
        super().setUp()
        self.db.drop_all()
        self.db.create_all()

        u1 = User(username="Conservator57")
        u2 = User(username="Analyst99")

        # sources
        dt = Bibl(abbr="DT01", bibl="DT de test")
        pouilles = Bibl(abbr="Pouillés", bibl="Exemplaire des Pouillés de test")

        # referenced sources
        dt_nopage = ReferencedByBibl(bibl=dt)
        dt_p1 = ReferencedByBibl(bibl=dt, num_start_page=1)
        pouilles_p10 = ReferencedByBibl(bibl=pouilles, num_start_page=10)

        # resp statements
        r1 = RespStatement(user=u2, resp="Analyst")
        r2 = RespStatement(user=u1, reference=dt_nopage, resp="Conservator")
        r3 = RespStatement(user=u1, reference=dt_p1, resp="Conservator")
        r4 = RespStatement(user=u2, reference=pouilles_p10, resp="Analyst")

        # place
        p = Place(id="DT01-00001", country="fr", dpt="99", label="Laon", resp_stmt=r3)

        # attach the citable elements to the palce
        data = [("description", "Ferme"), ("comment", "Ferme détruite après incendie")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r1))

        data = [("description", "Ferme réduite à l'état de ruine"),
                ("comment", "Ferme détruite après l'incendie qui ravagea toute la ville de Laon en 1857")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r2))

        data = [("description", "Ferme en partie détruite par le feu")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r3))

        data = [("description", "Ancienne ferme transformée en moulin")]
        for key, value in data:
            PlaceCitableElement(p, CitableElement(key=key, value=value, resp_stmt=r4))

        oldlabel_dt = PlaceOldLabel(old_label_id='OLD-001', place=p, resp_stmt=r3, rich_label="Lodanium")
        old_label_pouilles = PlaceOldLabel(old_label_id='OLD-002', place=p, resp_stmt=r4, rich_label="Lodanivm")

        self.db.session.add(p)
        self.db.session.commit()

    def test_source_differenciation(self):
        p = Place.query.first()

        #==========================
        # Pouillés
        #==========================
        print("=" * 80, "\nCitable elements filtered by source 'Pouillés'")
        print("=" * 80)
        for citable in p.citable_elements_filtered_by_source('Pouillés'):
            print("{0}: '{1}'\n\t{2}\n".format(citable.key, citable.value, citable.resp_stmt))

        print("----- old labels -------")
        for old_label in p.old_labels_filtered_by_source('Pouillés'):
            print('\t(old_label: {0}, {1}'.format(old_label.rich_label, old_label.resp_stmt))

        #==========================
        # DicoTopo
        #==========================
        print("=" * 80, "\nCitable elements filtered by source 'DT01'")
        print("=" * 80)
        for citable in p.citable_elements_filtered_by_source('DT01'):
            print("{0}: '{1}'\n\t{2}\n".format(citable.key, citable.value, citable.resp_stmt))

        print("----- old labels -------")
        for old_label in p.old_labels_filtered_by_source('DT01'):
            print('\t(old_label: {0}, {1}'.format(old_label.rich_label, old_label.resp_stmt))
