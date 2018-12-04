from app import db
from app.api.feature_type.facade import FeatureTypeFacade
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade
from app.api.placename.facade import PlacenameFacade, PlacenameSearchFacade
from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
from app.api.placename_old_label.facade import PlacenameOldLabelFacade, PlacenameOldLabelSearchFacade

from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, fields=None, page=None, per_page=None, index=None):

        # by default, search on the model table
        # custom index allow to use multiple indexes: index="table1,table2,table3..."
        if index is None:
            index = cls.__tablename__

        # perform the query
        #print(page, per_page)
        results, total = query_index(index=index, query=expression,
                                 fields=fields, page=page, per_page=per_page)
        #print(expression, results, total)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []

        ids = [r["id"] for r in results[index]]

        if len(ids) == 0:
            return cls.query.filter_by(id=0), 0

        for i in range(len(ids)):
            when.append((ids[i], i))

        #print("test")
        #print("when:", when)
        #for idx in index.split(","):
        #    obj = db.session.query(MODELS_HASH_TABLE[idx]).filter()
        #    print(idx, obj)
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Placename(SearchableMixin, db.Model):
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
    __searchable__ = ['label']
    __jsonapi_search_facade__ = PlacenameSearchFacade

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


class PlacenameAltLabel(SearchableMixin, db.Model):
    """ """
    __tablename__ = 'placename_alt_label'
    __jsonapi_search_facade__ = PlacenameAltLabelFacade

    __table_args__ = (
        db.UniqueConstraint('placename_id', 'label', name='_placename_label_uc'),
    )
    __searchable__ = ['label']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placename_id = db.Column(db.String(10), db.ForeignKey(Placename.id), index=True)
    label = db.Column(db.String(200))

    # relationships
    placename = db.relationship(Placename, backref=db.backref('alt_labels'))


class PlacenameOldLabel(SearchableMixin, db.Model):
    """ """
    __tablename__ = 'placename_old_label'
    __jsonapi_search_facade__ = PlacenameOldLabelSearchFacade

    __searchable__ = ['text_label_node']

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


class InseeCommune(SearchableMixin, db.Model):
    """ """
    __tablename__ = 'insee_commune'
    __jsonapi_search_facade__ = CommuneFacade

    __searchable__ = ['NCCENR']

    id = db.Column("insee_code", db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False, index=True)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False, index=True)
    AR_id = db.Column(db.String(8), db.ForeignKey('insee_ref.id'), index=True)
    CT_id = db.Column(db.String(9), db.ForeignKey('insee_ref.id'), index=True)
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    # relationships
    region = db.relationship('InseeRef', primaryjoin="InseeCommune.REG_id==InseeRef.id", backref=db.backref('communes_region'))
    departement = db.relationship('InseeRef', primaryjoin="InseeCommune.DEP_id==InseeRef.id", backref=db.backref('communes_departement'))
    arrondissement = db.relationship('InseeRef', primaryjoin="InseeCommune.AR_id==InseeRef.id", backref=db.backref('communes_arrondissement'))
    canton = db.relationship('InseeRef', primaryjoin="InseeCommune.CT_id==InseeRef.id", backref=db.backref('communes_canton'))


class InseeRef(SearchableMixin, db.Model):
    """ """
    __tablename__ = 'insee_ref'
    __jsonapi_search_facade__ = InseeRefFacade

    __searchable__ = ['label']

    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(4), nullable=False, index=True)
    insee_code = db.Column(db.String(3), nullable=False, index=True)
    parent_id = db.Column(db.String(10), db.ForeignKey('insee_ref.id'), index=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    label = db.Column(db.String(50), nullable=False)

    # relationships
    children = db.relationship("InseeRef", backref=db.backref('parent', remote_side=[id]))


class FeatureType(SearchableMixin, db.Model):
    """ """
    __tablename__ = 'feature_type'
    __jsonapi_search_facade__ = FeatureTypeFacade

    __table_args__ = (
        db.UniqueConstraint('placename_id', 'term', name='_placename_term_uc'),
    )
    __searchable__ = ['term']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placename_id = db.Column(db.String(10), db.ForeignKey('placename.placename_id'), index=True)
    term = db.Column(db.String(400))

    # relationships
    placename = db.relationship(Placename, backref=db.backref('feature_types'))
