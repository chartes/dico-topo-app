import datetime
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.ext.declarative import declared_attr

from app import db


class CitableElementMixin(object):

    @declared_attr
    def responsibility_id(cls):
        return db.Column(db.Integer, db.ForeignKey('responsibility.id'), nullable=False)

    @declared_attr
    def responsibility(cls):
        return db.relationship("Responsibility")

    def filter_by_source(self, abbr_src):
        return (abbr_src is None and self.responsibility.bibl is None) or (self.responsibility.bibl and self.responsibility.bibl.abbr == abbr_src)


def related_to_place_mixin(backref_name=None):
    class RelatedToPlaceMixin(object):
        @declared_attr
        def place_id(cls):
            return db.Column(db.String(10), db.ForeignKey('place.place_id'), nullable=False, index=True)

        @declared_attr
        def place(cls):
            if backref_name:
                return db.relationship("Place", backref=db.backref(backref_name))
            return db.relationship("Place")
    return RelatedToPlaceMixin


class Place(CitableElementMixin, db.Model):
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
    __tablename__ = 'place'

    id = db.Column("place_id", db.String(10), primary_key=True)
    label = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    dpt = db.Column(db.String(2), nullable=False)
    # not null if the place is known as being a commune
    commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    # not null if the place is localized somewhere
    localization_commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    # type of relation (Getty Vocabulary) between the place and the commune of location
    localization_commune_relation_type = db.Column(db.Enum('tgn3000_related_to', 'broaderPartitive'))

    # first num of the page where the place appears (within its source)
    #num_start_page = db.Column(db.Integer, index=True)

    # relationships
    commune = db.relationship(
        'InseeCommune', backref=db.backref('place', uselist=False),
        primaryjoin="InseeCommune.id==Place.commune_insee_code",
        uselist=False,
    )
    localization_commune = db.relationship(
        'InseeCommune', backref=db.backref('localized_places'),
        primaryjoin="InseeCommune.id==Place.localization_commune_insee_code",
        uselist=False
    )

    #linked_places = db.relationship('Place')

    @property
    def linked_places(self):
        co = self.related_commune
        if co:
            return Place.query.filter(Place.localization_commune_insee_code == co.id, Place.id != self.id).all()
        else:
            return []

    @property
    def related_commune(self):
        if self.commune:
            return self.commune
        elif self.localization_commune:
            return self.localization_commune
        else:
            return None

    @property
    def longlat(self):
        co = self.related_commune
        return co.longlat if co else None


class PlaceDescription(CitableElementMixin, related_to_place_mixin("descriptions"), db.Model):
    __tablename__ = "place_description"
    __table_args__ = (
        db.UniqueConstraint('place_id', 'responsibility_id', name='_place_desc_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)


class PlaceComment(CitableElementMixin, related_to_place_mixin("comments"), db.Model):
    __tablename__ = "place_comment"
    __table_args__ = (
        db.UniqueConstraint('place_id', 'responsibility_id', name='_place_comment_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)


class PlaceAltLabel(CitableElementMixin, related_to_place_mixin("alt_labels"), db.Model):
    """ """
    __tablename__ = 'place_alt_label'
    __table_args__ = (
        db.UniqueConstraint('place_id', 'label', name='_place_label_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(200))


class PlaceOldLabel(CitableElementMixin, related_to_place_mixin("old_labels"), db.Model):
    """ """
    __tablename__ = 'place_old_label'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    old_label_id = db.Column(db.String(13), nullable=False, unique=True)

    rich_label = db.Column(db.String(250), nullable=False)
    # date with tags
    rich_date = db.Column(db.String(100))
    # date wo tags
    text_date = db.Column(db.String(100))
    # primary source reference with tags
    rich_reference = db.Column(db.Text)
    # full old label with tags
    rich_label_node = db.Column(db.Text)

    @property
    def longlat(self):
        return self.place.longlat

    @property
    def label(self):
        return self.rich_label


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
    siaf_id = db.Column(db.String(64))

    # relationships
    region = db.relationship('InseeRef', primaryjoin="InseeCommune.REG_id==InseeRef.id",
                             backref=db.backref('communes_region'))
    departement = db.relationship('InseeRef', primaryjoin="InseeCommune.DEP_id==InseeRef.id",
                                  backref=db.backref('communes_departement'))
    arrondissement = db.relationship('InseeRef', primaryjoin="InseeCommune.AR_id==InseeRef.id",
                                     backref=db.backref('communes_arrondissement'))
    canton = db.relationship('InseeRef', primaryjoin="InseeCommune.CT_id==InseeRef.id",
                             backref=db.backref('communes_canton'))


class InseeRef(db.Model):
    """ """
    __tablename__ = 'insee_ref'

    id = db.Column(db.String(10), primary_key=True)
    # 'CTNP' for "Canton non précisé": https://www.insee.fr/fr/information/2560628#ct
    type = db.Column(db.String(4), CheckConstraint('type IN ("PAYS","REG","DEP", "AR", "CT", "CTNP")'), nullable=False,
                     index=True)
    insee_code = db.Column(db.String(3), nullable=False, index=True)
    parent_id = db.Column(db.String(10), db.ForeignKey('insee_ref.id'), index=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    label = db.Column(db.String(50), nullable=False)

    # relationships
    children = db.relationship("InseeRef", backref=db.backref('parent', remote_side=[id]))


class PlaceFeatureType(CitableElementMixin, related_to_place_mixin("place_feature_types"), db.Model):
    """ """
    __tablename__ = 'place_feature_type'
    __table_args__ = (
        db.UniqueConstraint('place_id', 'term', name='_place_term_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = db.Column(db.String(400))


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Bibl(db.Model):
    """ """
    __tablename__ = 'bibl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    abbr = db.Column(db.String(20), nullable=False)
    bibl = db.Column(db.Text, nullable=False)
    bnf_catalogue_ark = db.Column(db.String(30))
    gallica_ark = db.Column(db.String(30))
    gallica_page_one = db.Column(db.String(15))
    gallica_IIIF_availability = db.Column(db.Boolean)

    def __repr__(self):
        return '{0}'.format(self.abbr)


class Responsibility(db.Model):
    __tablename__ = "responsibility"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    bibl_id = db.Column(db.Integer, db.ForeignKey('bibl.id'), nullable=True, index=True)

    # first num of the page where the element appears (within its source)
    num_start_page = db.Column(db.Integer, nullable=True)

    creation_date = db.Column(DATETIME(storage_format="%(year)04d-%(month)02d-%(day)02dT%(hour)02d:%(minute)02d:%(second)02d",
                                          regexp=r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)"), default=datetime.datetime.utcnow)

    user = db.relationship("User", backref=db.backref('responsibilities'))
    bibl = db.relationship("Bibl")

    def __repr__(self):
        return '{1}, page:{0}, created-at:{2}, created-by:{3}'.format(
            self.num_start_page,
            self.bibl,
            self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.user.username
        )
