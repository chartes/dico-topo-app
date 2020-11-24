import pprint
import random

from app.cli import make_cli

from app.models import Place, User, Bibl, Responsibility, \
    PlaceOldLabel, PlaceDescription, PlaceComment, IdRegister
from tests.base_server import TestBaseServer
from click.testing import CliRunner


class TestIdGen(TestBaseServer):

    def setUp(self):
        super().setUp()

        self.cli = make_cli(self.app)
        self.cli_runner = CliRunner()

        self.db.drop_all()
        self.db.create_all()

        u1 = User(username="Conservator57")

        # sources
        dt = Bibl(abbr="DT01", bibl="DT de test")

        # resp statements
        r3 = Responsibility(user=u1, bibl=dt, num_start_page=1)
        self.db.session.add(r3)
        self.db.session.add(u1)
        self.db.session.add(dt)

        self.db.session.commit()

        # places
        places = []
        for i in range(1, 1000):
            p = Place(id="DT01-%s" % (str(i).zfill(10)), country="fr", dpt="99", label="Metz")
            p.responsibility_id = r3.id
            places.append(p)
            self.db.session.add(p)

        self.db.session.flush()

        # attach the citable elements to the palce
        for desc, responsibility in [
            ("Ferme en partie détruite par le feu", r3),
        ]:
            p_desc = PlaceDescription()
            p_desc.content = desc
            p_desc.place = places[0]
            p_desc.responsibility = responsibility
            self.db.session.add(p_desc)

        for comment, responsibility in [
            ("L'incendie de 1857 qui frappa Laon fit s'éffondrer le toit de la ferme", r3),
        ]:
            p_comm = PlaceComment()
            p_comm.content = comment
            p_comm.place = places[0]
            p_comm.responsibility = responsibility
            self.db.session.add(p_comm)

        self.db.session.commit()

    def test_clear(self):
        result = self.cli_runner.invoke(self.cli, ['id-register', '--clear'], input='y')
        assert result.exit_code == 0
        print(result.output)

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

    def test_append_id_max(self):
        self.cli = make_cli(self.app)
        result = self.cli_runner.invoke(self.cli, ['id-register', '--append'], input='y')
        assert result.exit_code == 0
        with self.assertRaises(ValueError):
            result.output.rindex('There is (probably) no room anymore!')

    def test_append_from_scratch(self):
        result = self.cli_runner.invoke(self.cli, ['id-register', '--clear', '--append'], input='y')
        #assert result.exit_code == 0
        print(result.output)

    def test_append_with_non_empty(self):
        pass

    def test_append_when_already_in_db(self):
        pass

    def test_append_with_already_newid_format(self):
        pass
