import datetime

from app import db
from flask_user import UserMixin


class Placename(db.Model):
    """Illustrate class-level docstring.

    Classes use a special whitespace convention: the opening and closing quotes
    are preceded and followed by a blank line, respectively. No other
    docstrings should be preceded or followed by anything but code.

    A blank line at the end of a multi-line docstring before the closing
    quotation marks simply makes it easier for tooling to auto-format
    paragraphs (wrapping them at 79 characters, per PEP8), without the closing
    quotation marks interfering. For example, in Vim, you can use `gqip` to
    "apply text formatting inside the paragraph." In Emacs, the equivalent
    would be the `fill-paragraph` command. While it's not required, the
    presence of a blank line is quite common and much appreciated. Regardless,
    the closing quotation marks should certainly be on a line by themselves.

    """
    __tablename__ = 'placename'

    id = db.Column("placename_id", db.String(10), primary_key=True)
    label = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    dpt = db.Column(db.String(2), nullable=False)
    # not null if the placename is known as being commune
    commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    # not null if the placename is localized somewhere
    localization_commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    localization_placename_id = db.Column(db.String(10), db.ForeignKey('placename.placename_id'), index=True)
    localization_certainty = db.Column(db.Enum('high', 'low'))
    # description of the placename
    desc = db.Column(db.Text)
    # first num of the page where the placename appears (within its source)
    num_start_page = db.Column(db.Integer, index=True)
    # comment on the placename
    comment = db.Column(db.Text)

    # relationships
    commune = db.relationship(
        'InseeCommune', backref=db.backref('placename', uselist=False),
        primaryjoin="InseeCommune.id==Placename.commune_insee_code",
        uselist=False
    )
    localization_commune = db.relationship(
        'InseeCommune', backref=db.backref('localized_placenames'),
        primaryjoin="InseeCommune.id==Placename.localization_commune_insee_code",
        uselist=False
    )
    linked_placenames = db.relationship('Placename')


class PlacenameAltLabel(db.Model):
    """ """
    __tablename__ = 'placename_alt_label'
    __table_args__ = (
        db.UniqueConstraint('placename_id', 'label', name='_placename_label_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placename_id = db.Column(db.String(10), db.ForeignKey(Placename.id), index=True)
    label = db.Column(db.String(200))

    # relationships
    placename = db.relationship(Placename, backref=db.backref('alt_labels'))


class PlacenameOldLabel(db.Model):
    """ """
    __tablename__ = 'placename_old_label'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    old_label_id = db.Column(db.String(13), nullable=False, unique=True)
    placename_id = db.Column(db.String(10), db.ForeignKey('placename.placename_id'), nullable=False, index=True)
    rich_label = db.Column(db.String(250), nullable=False)
    # date with tags
    rich_date = db.Column(db.String(100))
    # date wo tags
    text_date = db.Column(db.String(100))
    # bibl reference with tags
    rich_reference = db.Column(db.Text)
    # full old label with tags
    rich_label_node = db.Column(db.Text)
    # full old label wo tags
    text_label_node = db.Column(db.Text)

    # relationships
    placename = db.relationship(Placename, backref=db.backref('old_labels'))


class InseeCommune(db.Model):
    """ """
    __tablename__ = 'insee_commune'

    id = db.Column("insee_code", db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False, index=True)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False, index=True)
    AR_id = db.Column(db.String(8), db.ForeignKey('insee_ref.id'), index=True)
    CT_id = db.Column(db.String(9), db.ForeignKey('insee_ref.id'), index=True)
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    geoname_id = db.Column(db.String(32))
    wikidata_item_id = db.Column(db.String(32))
    wikipedia_url = db.Column(db.String(512))
    databnf_ark = db.Column(db.String(64))
    viaf_id = db.Column(db.String(64))

    # relationships
    region = db.relationship('InseeRef', primaryjoin="InseeCommune.REG_id==InseeRef.id", backref=db.backref('communes_region'))
    departement = db.relationship('InseeRef', primaryjoin="InseeCommune.DEP_id==InseeRef.id", backref=db.backref('communes_departement'))
    arrondissement = db.relationship('InseeRef', primaryjoin="InseeCommune.AR_id==InseeRef.id", backref=db.backref('communes_arrondissement'))
    canton = db.relationship('InseeRef', primaryjoin="InseeCommune.CT_id==InseeRef.id", backref=db.backref('communes_canton'))


class InseeRef(db.Model):
    """ """
    __tablename__ = 'insee_ref'

    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(4), nullable=False, index=True)
    insee_code = db.Column(db.String(3), nullable=False, index=True)
    parent_id = db.Column(db.String(10), db.ForeignKey('insee_ref.id'), index=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    label = db.Column(db.String(50), nullable=False)

    # relationships
    children = db.relationship("InseeRef", backref=db.backref('parent', remote_side=[id]))


class FeatureType(db.Model):
    """ """
    __tablename__ = 'feature_type'
    __table_args__ = (
        db.UniqueConstraint('placename_id', 'term', name='_placename_term_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placename_id = db.Column(db.String(10), db.ForeignKey('placename.placename_id'), index=True)
    term = db.Column(db.String(400))

    # relationships
    placename = db.relationship(Placename, backref=db.backref('feature_types'))



class User(db.Model, UserMixin):
    """ Utilisateur """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User authentication information
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(), nullable=False, unique=True)
    email_confirmed_at = db.Column('confirmed_at', db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column('firstname', db.String(), nullable=False, server_default='')
    last_name = db.Column('lastname', db.String(), nullable=False, server_default='')

    roles = db.relationship('UserRole', secondary='user_has_role')

    @staticmethod
    def add_default_users():
        admin = UserRole.query.filter(UserRole.name == "admin").first()
        contributor = UserRole.query.filter(UserRole.name == "contributor").first()
        password = "pbkdf2:sha256:50000$RyjGxAYv$02c62c497306be557eb4080a432c466453f297eb9dbfb62dc0160fe376f22689" # Lettres2019!
        db.session.add(User(username="admin",
                            password=password,
                            email="admin.lettres@chartes.psl.eu",
                            active=True,
                            email_confirmed_at=datetime.datetime.now(),
                            roles=[admin, contributor]))

        db.session.add(User(username="contributor",
                            password=password,
                            email="contributor.lettres@chartes.psl.eu",
                            active=True,
                            email_confirmed_at=datetime.datetime.now(),
                            roles=[contributor]))

    def to_json(self):
        return {
            "username": self.username,
            "roles": [r.name for r in self.roles]
        }


class UserRole(db.Model):
    """ Rôle des utilisateurs (administrateur ou contributeur) """
    __tablename__ = 'user_role'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))

    @staticmethod
    def add_default_roles():
        db.session.add(UserRole(name="admin", description="Administrator"))
        db.session.add(UserRole(name="contributor", description="Contributor"))


class UserHasRole(db.Model):
    __tablename__ = 'user_has_role'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('user_role.id', ondelete='CASCADE'))


class UserInvitation(db.Model):
    __tablename__ = 'user_invitation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # UserInvitation email information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False)
    # save the user of the invitee
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
