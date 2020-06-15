import pprint

from app.api.place.facade import PlaceFacade
from app.models import Place, User, Bibl, RespStatement, \
    PlaceOldLabel, PlaceDescription, PlaceComment
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
        pages_jaunes = Bibl(abbr="PagesJaunes", bibl="Exemplaire des Pages Jaunes de test")

        # resp statements
        r1 = RespStatement(user=u2)
        r2 = RespStatement(user=u1, bibl=pages_jaunes, num_start_page=None)
        r3 = RespStatement(user=u1, bibl=dt, num_start_page=1)
        r4 = RespStatement(user=u2, bibl=pouilles, num_start_page=10)

        # place
        p = Place(id="DT01-00001", country="fr", dpt="99", label="Laon", resp_stmt=r3)

        # attach the citable elements to the palce
        for desc, resp_stmt in [
            ("Ferme", r1),
            ("Ferme réduite à l'état de ruine", r2),
            ("Ferme en partie détruite par le feu", r3),
            ("Ancienne ferme transformée en moulin", r4)
        ]:
            p_desc = PlaceDescription()
            p_desc.content = desc
            p_desc.place = p
            p_desc.resp_stmt = resp_stmt

        for comment, resp_stmt in [
            ("L'incendie de 1857 qui frappa Laon fit s'éffondrer le toit de la ferme", r2),
            ("Aujourd'hui reconstruite et transformée en discothèque", r4)
        ]:
            p_comm = PlaceComment()
            p_comm.content = comment
            p_comm.place = p
            p_comm.resp_stmt = resp_stmt

        oldlabel_dt = PlaceOldLabel(old_label_id='OLD-001', place=p, resp_stmt=r3, rich_label="Lodanium")
        old_label_pouilles = PlaceOldLabel(old_label_id='OLD-002', place=p, resp_stmt=r4, rich_label="Lodanivm")

        self.db.session.add(p)
        self.db.session.commit()

    def test_source_differenciation(self):
        p = Place.query.first()

        #==========================
        # Pouillés
        #==========================
        print("=" * 80, "\nFiltre sur les données issues de la source secondaire 'Pouillés'")
        print("=" * 80)
        print("Responsabilité du lieu :", p.resp_stmt)
        print("-" * 80)

        for desc in [d for d in p.descriptions if d.filter_by_source("Pouillés")]:
            print("Description :", desc.content)
            print("\t Responsabilité :", desc.resp_stmt)

        for comment in [d for d in p.comments if d.filter_by_source("Pouillés")]:
            print("Commentaire :", comment.content)
            print("\t Responsabilité :", desc.resp_stmt)

        for old_label in [d for d in p.old_labels if d.filter_by_source("Pouillés")]:
            print("OldLabel :", old_label.rich_label)
            print("\t Responsabilité :", desc.resp_stmt)

        #==========================
        # DicoTopo
        #==========================
        print("=" * 80, "\nFiltre sur les données issues de la source secondaire 'DT01'")
        print("=" * 80)
        print("Responsabilité du lieu :", p.resp_stmt)
        print("-" * 80)

        for desc in [d for d in p.descriptions if d.filter_by_source("DT01")]:
            print("Description :", desc.content)
            print("\t Responsabilité :", desc.resp_stmt)

        for comment in [d for d in p.comments if d.filter_by_source("DT01")]:
            print("Commentaire :", comment.content)
            print("\t Responsabilité :", desc.resp_stmt)

        for old_label in [d for d in p.old_labels if d.filter_by_source("DT01")]:
            print("OldLabel :", old_label.rich_label)
            print("\t Responsabilité :", desc.resp_stmt)
