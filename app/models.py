from app import db


class Entry(db.Model):
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

    insee = db.relationship('InseeCommune', backref=db.backref('entries'),
                            primaryjoin="InseeCommune.insee_id==Entry.insee_id")
    localization_insee = db.relationship('InseeCommune', backref=db.backref('localization_entries'),
                                         primaryjoin="InseeCommune.insee_id==Entry.localization_insee_id")
    localization_entry = db.relationship('Entry', uselist=False)

    @property
    def resource_identifier(self):
        return {
            "type": "entries",
            "id": self.entry_id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                "orth": self.orth,
                "country": self.country,
                "dpt": self.dpt,
                "def": self.def_col,
                "localization-certainty": self.localization_certainty
            },
            "relationships": {
                "insee": {
                    "links": {
                        "self": "/entries/%s/relationships/insee" % self.entry_id,
                        "related": "/entries/%s/insee" % self.entry_id
                    },
                    "data": None if self.insee is None else self.insee.resource_identifier
                },
                "localization-insee": {
                    "links": {
                        "self": "/entries/%s/relationships/localization-insee" % self.entry_id,
                        "related": "/entries/%s/localization-insee" % self.entry_id
                    },
                    "data": None if self.localization_insee is None else self.localization_insee.resource_identifier
                },
                "localization-entry": {
                    "links": {
                        "self": "/entries/%s/relationships/localization-entry" % self.entry_id,
                        "related": "/entries/%s/localization-entry" % self.entry_id
                    },
                    "data": None if self.localization_entry is None else self.localization_entry.resource_identifier
                },
                "alt-orths": {
                    "links": {
                        "self": "/entries/%s/relationships/alt-orths" % self.entry_id,
                        "related": "/entries/%s/alt-orths" % self.entry_id
                    },
                    "data": [] if self.alt_orths is None else [_as.resource_identifier for _as in self.alt_orths]
                },
            },
            "meta": {},
            "links": {
                "self": "/entries/%s" % self.entry_id
            }
        }
        res.update(self.resource_identifier)
        return res


class AltOrth(db.Model):
    __tablename__ = 'alt_orth'
    entry_id = db.Column(db.String(10), db.ForeignKey(Entry.entry_id), primary_key=True)
    label = db.Column(db.String(200), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('alt_orths'))

    @property
    def resource_identifier(self):
        return {
            "type": "alt-orths",
            "id": self.entry_id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                "label": self.label
            },
            "relationships": {
                "entry": {
                    "links": {
                        "self": "/alt-orths/%s/relationships/entry" % self.entry_id,
                        "related": "/alt-orths/%s/entry" % self.entry_id
                    },
                    "data": self.entry.resource_identifier
                }
            },
            "meta": {},
            "links": {
                "self": "/alt-orths/%s" % self.entry_id
            }
        }
        res.update(self.resource_identifier)
        return res


class Keywords(db.Model):
    __tablename__ = 'keywords'
    entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), primary_key=True)
    term = db.Column(db.String(400), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('keywords'))

    @property
    def unique_id(self):
        return "%s_%s" % (self.entry_id, self.term)

    @property
    def resource_identifier(self):
        return {
            "type": "keywords",
            "id": self.unique_id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                "term": self.term
            },
            "relationships": {
                "entry": {
                    "self": "/keywords/%s/relationships/entry" % self.unique_id,
                    "related": "/keywords/%s/entry" % self.unique_id
                }
            },
            "meta": {},
            "links": {
                "self": "/keywords/%s" % self.unique_id
            }
        }
        res.update(self.resource_identifier)
        return res


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

    entry = db.relationship(Entry, backref=db.backref('old_orths'))

    @property
    def resource_identifier(self):
        return {
            "type": "old-orths",
            "id": self.id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                "orth": self.old_orth,
                "date-rich": self.date_rich,
                "date-nude": self.date_nude,
                "reference-rich": self.date_rich,
                "reference-nude": self.date_nude
            },
            "relationships": {
                "entry": {
                    "self": "/old-orths/%s/relationships/entry" % self.id,
                    "related": "/old-orths/%s/entry" % self.id
                },
                "old-orths": {
                    "self": "/old-orths/%s/relationships/old-orths" % self.id,
                    "related": "/old-orths/%s/old-orths" % self.id
                }
            },
            "meta": {},
            "links": {
                "self": "/old-orths/%s" % self.id
            }
        }
        res.update(self.resource_identifier)
        return res


class InseeCommune(db.Model):
    __tablename__ = 'insee_commune'
    insee_id = db.Column(db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False)
    AR_id = db.Column(db.String(8), db.ForeignKey('insee_ref.id'))
    CT_id = db.Column(db.String(9))
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    """
    REG = db.relationship('InseeRef', backref=db.backref('REG'),
                          primaryjoin="InseeCommune.REG_id==InseeRef.id")
    DEP = db.relationship('InseeRef', backref=db.backref('DEP'),
                          primaryjoin="InseeCommune.DEP_id==InseeRef.id")
    AR = db.relationship('InseeRef', backref=db.backref('AR'),
                         primaryjoin="InseeCommune.AR_id==InseeRef.id")
    """

    @property
    def resource_identifier(self):
        return {
            "type": "insee-communes",
            "id": self.insee_id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                'CT_id': self.CT_id,
                'NCCENR': self.NCCENR,
                'ARTMIN': self.ARTMIN,
                'longlat': self.longlat
            },
            "relationships": {
                "reg": {
                    "self": "/insee-communes/%s/relationships/reg" % self.insee_id,
                    "related": "/insee-communes/%s/reg" % self.insee_id
                },
                "dep": {
                    "self": "/insee-communes/%s/relationships/dep" % self.insee_id,
                    "related": "/insee-communes/%s/dep" % self.insee_id
                },
                "ar": {
                    "self": "/insee-communes/%s/relationships/ar" % self.insee_id,
                    "related": "/insee-communes/%s/ar" % self.insee_id
                }
            },
            "meta": {},
            "links": {
                "self": "/insee-communes/%s" % self.insee_id
            }
        }
        res.update(self.resource_identifier)
        return res


class InseeRef(db.Model):
    __tablename__ = 'insee_ref'
    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(4), nullable=False)
    insee = db.Column(db.String(3), nullable=False)
    parent_id = db.Column(db.String(10), db.ForeignKey('insee_ref.id'))
    level = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(50), nullable=False)

    children = db.relationship("InseeRef", backref=db.backref('parent', remote_side=[id]))

    @property
    def resource_identifier(self):
        return {
            "type": "insee-refs",
            "id": self.id
        }

    @property
    def resource(self):
        res = {
            "attributes": {
                'ref-type': self.type,
                'insee': self.insee,
                'level': self.level,
                'label': self.label
            },
            "relationships": {
                "parent": {
                    "self": "/insee-refs/%s/relationships/parent" % self.id,
                    "related": "/insee-refs/%s/parent" % self.id
                },
                "children": {
                    "self": "/insee-refs/%s/relationships/children" % self.id,
                    "related": "/insee-refs/%s/children" % self.id
                }
            },
            "meta": {},
            "links": {
                "self": "/insee-refs/%s" % self.id
            }
        }
        res.update(self.resource_identifier)
        return res
