from sqlalchemy import CheckConstraint
import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from app import db


class Place(db.Model):
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
    # not null if the place is known as being commune
    commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    # not null if the place is localized somewhere
    localization_commune_insee_code = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_code'), index=True)
    localization_place_id = db.Column(db.String(10), db.ForeignKey('place.place_id'), index=True)
    localization_certainty = db.Column(db.Enum('high', 'low'))
    # description of the place
    #desc = db.Column(db.Text)
    # first num of the page where the place appears (within its source)
    #num_start_page = db.Column(db.Integer, index=True)
    # comment on the place
    #comment = db.Column(db.Text)
    # id of the responsibility statement
    resp_stmt_id = db.Column(db.Integer,db.ForeignKey('resp_statement.id'), nullable=False)

    # relationships
    commune = db.relationship(
        'InseeCommune', backref=db.backref('place', uselist=False),
        primaryjoin="InseeCommune.id==Place.commune_insee_code",
        uselist=False
    )
    localization_commune = db.relationship(
        'InseeCommune', backref=db.backref('localized_places'),
        primaryjoin="InseeCommune.id==Place.localization_commune_insee_code",
        uselist=False
    )
    # responsibility statement of the place itself
    resp_stmt = db.relationship('RespStatement')
    # a list of citable elements
    citable_elements = association_proxy('citables', 'citable')

    linked_places = db.relationship('Place')

    @property
    def longlat(self):
        if self.commune:
            co = self.commune
        elif self.localization_commune:
            co = self.localization_commune
        else:
            co = None
        return co.longlat if co else None

    def citable_elements_filtered_by_source(self, abbr_src):
        return [
            el for el in self.citable_elements
            if el.resp_stmt.reference is None or (el.resp_stmt.reference and el.resp_stmt.reference.bibl.abbr == abbr_src)
        ]


class PlaceAltLabel(db.Model):
    """ """
    __tablename__ = 'place_alt_label'
    __table_args__ = (
        db.UniqueConstraint('place_id', 'label', name='_place_label_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.String(10), db.ForeignKey(Place.id), index=True)
    label = db.Column(db.String(200))

    # relationships
    place = db.relationship(Place, backref=db.backref('alt_labels'))


class PlaceOldLabel(db.Model):
    """ """
    __tablename__ = 'place_old_label'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    old_label_id = db.Column(db.String(13), nullable=False, unique=True)
    place_id = db.Column(db.String(10), db.ForeignKey('place.place_id'), nullable=False, index=True)
    resp_stmt_id = db.Column(db.Integer, db.ForeignKey('resp_statement.id'), nullable=False)

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

    # responsibility statement of the place itself
    resp_stmt = db.relationship('RespStatement')

    # relationships
    place = db.relationship(Place, backref=db.backref('old_labels'))

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


class FeatureType(db.Model):
    """ """
    __tablename__ = 'feature_type'
    __table_args__ = (
        db.UniqueConstraint('place_id', 'term', name='_place_term_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.String(10), db.ForeignKey('place.place_id'), index=True)
    term = db.Column(db.String(400))

    # relationships
    place = db.relationship(Place, backref=db.backref('feature_types'))


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)


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


class ReferencedByBibl(db.Model):
    __tablename__ = "referenced_by_bibl"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    bibl_id = db.Column(db.Integer, db.ForeignKey('bibl.id'), nullable=False)
    # first num of the page where the element appears (within its source)
    num_start_page = db.Column(db.Integer, nullable=True)

    bibl = db.relationship("Bibl")

    def __repr__(self):
        return '(source:{1}, page:{0})'.format(
            self.num_start_page,
            self.bibl
        )


class RespStatement(db.Model):
    __tablename__ = "resp_statement"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ref_id = db.Column(db.Integer, db.ForeignKey('referenced_by_bibl.id'), nullable=True)

    # see http://www.loc.gov/marc/relators/relacode.html and https://tei-c.org/release/doc/tei-p5-doc/fr/html/ref-resp.html
    resp = db.Column(db.String, db.Enum("Abridger", "Art copyist", "Analyst", "Conservator"),
                     nullable=False, index=True)
    note = db.Column(db.Text)

    user = db.relationship("User")
    reference = db.relationship("ReferencedByBibl", backref=db.backref('referrer', uselist=False))

    def __repr__(self):
        return 'from:{0}, {1}, referenced-by:{2}'.format(
            self.user.username if self.user else None,
            self.resp,
            self.reference
        )


class CitableElement(db.Model):
    __tablename__ = "citable_element"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(20), nullable=False) # add constraint 'key in (...)' ?
    value = db.Column(db.Text, nullable=True)

    resp_stmt_id = db.Column(db.Integer, db.ForeignKey('resp_statement.id'), nullable=False)
    resp_stmt = db.relationship("RespStatement")

    def __repr__(self):
        return 'CitableElement: (key: {0}, value: {1})'.format(self.key, self.value)


class PlaceCitableElement(db.Model):
    __tablename__ = "place_citable_element"
    __table_args__ = (
        db.UniqueConstraint('place_id', 'citable_id', name='_place_id_citable_id_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.Integer, db.ForeignKey('place.place_id'), nullable=False)
    citable_id = db.Column(db.Integer, db.ForeignKey('citable_element.id'), nullable=False)

    # bidirectional place/citables relationships, mapping
    place = db.relationship("Place", backref=db.backref("citables", cascade="all, delete-orphan"))
    citable = db.relationship("CitableElement")

    def __init__(self, place, citable):
        self.place = place
        self.citable = citable
