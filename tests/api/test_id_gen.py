import pprint

from app.models import Place, User, Bibl, Responsibility, \
    PlaceOldLabel, PlaceDescription, PlaceComment, IdRegister
from tests.base_server import TestBaseServer
from click.testing import CliRunner


class TestIdGen(TestBaseServer):

    def setUp(self):
        super().setUp()

        from app.cli import make_cli
        self.cli = make_cli(self.app)
        self.cli_runner = CliRunner()

        self.db.drop_all()
        self.db.create_all()

        u1 = User(username="Conservator57")

        # sources
        dt = Bibl(abbr="DT01", bibl="DT de test")

        # resp statements
        r3 = Responsibility(user=u1, bibl=dt, num_start_page=1)

        # places
        p1 = Place(id="DT01-00001", country="fr", dpt="99", label="Metz", responsibility=r3)
        p2 = Place(id="DT01-00002", country="fr", dpt="99", label="Paris", responsibility=r3)
        p3 = Place(id="DT01-00003", country="fr", dpt="99", label="Montpellier", responsibility=r3)

        # attach the citable elements to the palce
        for desc, responsibility in [
            ("Ferme en partie détruite par le feu", r3),
        ]:
            p_desc = PlaceDescription()
            p_desc.content = desc
            p_desc.place = p1
            p_desc.responsibility = responsibility
            self.db.session.add(p_desc)

        for comment, responsibility in [
            ("L'incendie de 1857 qui frappa Laon fit s'éffondrer le toit de la ferme", r3),
        ]:
            p_comm = PlaceComment()
            p_comm.content = comment
            p_comm.place = p1
            p_comm.responsibility = responsibility
            self.db.session.add(p_comm)

        oldlabel_dt1 = PlaceOldLabel(old_label_id='OLD-001', place=p1, responsibility=r3, rich_label="Lodanium")
        oldlabel_dt2 = PlaceOldLabel(old_label_id='OLD-002', place=p1, responsibility=r3, rich_label="Lodanium")
        oldlabel_dt3 = PlaceOldLabel(old_label_id='OLD-003', place=p2, responsibility=r3, rich_label="Lodanium")

        self.db.session.add(u1)
        self.db.session.add(r3)
        self.db.session.add(dt)
        self.db.session.add(oldlabel_dt1)
        self.db.session.add(oldlabel_dt2)
        self.db.session.add(oldlabel_dt3)
        self.db.session.add(p1)
        self.db.session.add(p2)
        self.db.session.add(p3)
        self.db.session.commit()

    def test_rollback(self):
        result = self.cli_runner.invoke(self.cli, ['id-register', '--register'], input='n')
        assert result.exit_code == 0
        reg = IdRegister.query.all()
        self.assertEqual(len(reg), 0)

    def test_register(self):
        result = self.cli_runner.invoke(self.cli, ['id-register', '--register'], input='y')
        assert result.exit_code == 0
        reg = IdRegister.query.all()
        places = Place.query.all()

        self.assertEqual(len(reg), len(places))
        self.assertListEqual([p.id for p in places], [r.primary_value for r in reg])
        self.assertListEqual([r.primary_value for r in reg], [r.secondary_value for r in reg])

    def test_append_from_scratch(self):
        pass

    def test_append_with_non_empty(self):
        pass

    def test_append_when_already_in_db(self):
        pass

    def test_append_with_already_newid_format(self):
        pass
