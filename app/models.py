
from app import db


class Entry(db.Model):

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

    __tablename__ = 'entry'
    entry_id = db.Column(db.String(10), primary_key=True)
    orth = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    dpt = db.Column(db.String(2), nullable=False)
    insee_id = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_id'))
    localization_insee_id = db.Column(db.String(5), db.ForeignKey('insee_commune.insee_id'), index=True)
    localization_entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), index=True)
    localization_certainty = db.Column(db.Enum('high', 'low'))
    def_col = db.Column('def', db.String(200))
    start_pg = db.Column(db.Integer)

    commune = db.relationship('InseeCommune', backref=db.backref('placenames'),
                            primaryjoin="InseeCommune.insee_id==Entry.insee_id")
    localization_commune = db.relationship('InseeCommune', backref=db.backref('localized_placenames'),
                                         primaryjoin="InseeCommune.insee_id==Entry.localization_insee_id")
    localization_placename = db.relationship('Entry')


class AltOrth(db.Model):
    """ """
    __tablename__ = 'alt_orth'
    entry_id = db.Column(db.String(10), db.ForeignKey(Entry.entry_id), primary_key=True)
    alt_orth = db.Column(db.String(200), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('alt_orths'))


class Keywords(db.Model):
    """ """
    __tablename__ = 'keywords'
    entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), primary_key=True)
    term = db.Column(db.String(400), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('keywords'))


class OldOrth(db.Model):
    """ """
    __tablename__ = 'old_orth'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    old_orth_id = db.Column(db.String(13), nullable=False, unique=True)
    entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), nullable=False)
    old_orth = db.Column(db.String(250), nullable=False)
    date_rich = db.Column(db.String(100))
    date_nude = db.Column(db.String(100))
    reference_rich = db.Column(db.Text)
    reference_nude = db.Column(db.Text)
    full_old_orth_html = db.Column(db.Text)
    full_old_orth_nude = db.Column(db.Text)

    entry = db.relationship(Entry, backref=db.backref('old_orths'))


class InseeCommune(db.Model):
    """ """
    __tablename__ = 'insee_commune'
    insee_id = db.Column(db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False)
    AR_id = db.Column(db.String(8), db.ForeignKey('insee_ref.id'))
    CT_id = db.Column(db.String(9), db.ForeignKey('insee_ref.id'))
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    region = db.relationship('InseeRef', primaryjoin="InseeCommune.REG_id==InseeRef.id")
    departement = db.relationship('InseeRef',  primaryjoin="InseeCommune.DEP_id==InseeRef.id")
    arrondissement = db.relationship('InseeRef', primaryjoin="InseeCommune.AR_id==InseeRef.id")
    canton = db.relationship('InseeRef', primaryjoin="InseeCommune.CT_id==InseeRef.id")


class InseeRef(db.Model):
    """ """
    __tablename__ = 'insee_ref'
    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(4), nullable=False)
    insee = db.Column(db.String(3), nullable=False)
    parent_id = db.Column(db.String(10), db.ForeignKey('insee_ref.id'))
    level = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(50), nullable=False)

    children = db.relationship("InseeRef", backref=db.backref('parent', remote_side=[id]))
