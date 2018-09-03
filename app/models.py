
from app import db


class Entry(db.Model):
    entry_id = db.Column(db.CHAR(10), primary_key=True)
    orth = db.Column(db.VARCHAR(200), nullable=False)
    country = db.Column(db.CHAR(2), nullable=False)
    dpt = db.Column(db.CHAR(2), nullable=False)
    insee = db.Column(db.CHAR(5))
    localization_insee = db.Column(db.VARCHAR(250), index=True)
    localization_entry_id = db.Column(db.CHAR(10))
    localization_certainty = db.Column(db.Enum('high', 'low'))
    def_col = db.Column("def", db.VARCHAR(200))

    # TODO
    # FOREIGN KEY(insee)  REFERENCES  insee_communes(insee_id),
    # FOREIGN KEY(localization_insee) REFERENCES insee_communes(insee_id)

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
    entry_id = db.Column(db.CHAR(10), db.ForeignKey(Entry.entry_id), primary_key=True)
    label = db.Column(db.VARCHAR(200))

    entry = db.relationship(Entry, backref=db.backref('alt_orths'))

    def serialize(self):
        return {
            'entry': self.entry.serialize(),
            'label': self.label
        }
