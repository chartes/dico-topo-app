from app import db


class Entry(db.Model):
    __tablename__ = 'entry'
    entry_id = db.Column(db.String(10), primary_key=True)
    orth = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    dpt = db.Column(db.String(2), nullable=False)
    insee = db.Column(db.String(5), db.ForeignKey('insee_communes.insee_id'))
    localization_insee = db.Column(db.String(5), db.ForeignKey('insee_communes.insee_id'), index=True)
    localization_entry_id = db.Column(db.String(10))
    localization_certainty = db.Column(db.Enum('high', 'low'))
    def_col = db.Column('def', db.String(200))

    def serialize(self):
        return {
            'entry_id': self.entry_id,
            'orth': self.orth,
            'country': self.country,
            'dpt': self.dpt,
            'insee': self.insee,
            'localization_insee': self.localization_insee,
            'localization_entry_id': self.localization_entry_id,
            'localization_certainty': self.localization_certainty,
            'def': self.def_col
        }


class AltOrth(db.Model):
    __tablename__ = 'alt_orth'
    entry_id = db.Column(db.String(10), db.ForeignKey(Entry.entry_id), primary_key=True)
    label = db.Column(db.String(200))

    entry = db.relationship(Entry, backref=db.backref('alt_orths'))

    def serialize(self):
        return {
            'entry': self.entry.serialize(),
            'label': self.label
        }


class Keywords(db.Model):
    __tablename__ = 'keywords'
    entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), primary_key=True)
    term = db.Column(db.String(400), primary_key=True)


class OldOrth(db.Model):
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

    def serialize(self):
        return {
            'old_orth_id': self.old_orth_id,
            'entry_id': self.entry_id,
            'old_orth': self.old_orth,
            'date_rich': self.date_rich,
            'reference_rich': self.reference_rich
        }


class InseeCommunes(db.Model):
    __tablename__ = 'insee_communes'
    insee_id = db.Column(db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False)
    AR_id  = db.Column(db.String(8), db.ForeignKey('insee_ref.id'))
    CT_id  = db.Column(db.String(9))
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    def serialize(self):
        return {
            'insee_id': self.insee_id,
            'REG_id': self.REG_id,
            'DEP_id': self.DEP_id,
            'AR_id': self.AR_id,
            'CT_id': self.CT_id,
            'NCCENR': self.NCCENR,
            'ARTMIN': self.ARTMIN,
            'longlat': self.longlat
        }


class InseeRef(db.Model):
    __tablename__ = 'insee_ref'
    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(4), nullable=False)
    insee = db.Column(db.String(3), nullable=False)
    parent_id = db.Column(db.String(10))
    level = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(50), nullable=False)