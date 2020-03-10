import datetime

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
    desc = db.Column(db.Text)
    # first num of the page where the place appears (within its source)
    num_start_page = db.Column(db.Integer, index=True)
    # comment on the place
    comment = db.Column(db.Text)

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
        db.UniqueConstraint('place_id', 'term', name='_place_term_uc'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.String(10), db.ForeignKey('place.place_id'), index=True)
    term = db.Column(db.String(400))

    # relationships
    place = db.relationship(Place, backref=db.backref('feature_types'))

