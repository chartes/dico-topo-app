from flask import current_app

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

    insee = db.relationship('InseeCommune', backref=db.backref('entries'),
                            primaryjoin="InseeCommune.insee_id==Entry.insee_id")
    localization_insee = db.relationship('InseeCommune', backref=db.backref('localization_entries'),
                                         primaryjoin="InseeCommune.insee_id==Entry.localization_insee_id")
    localization_entry = db.relationship('Entry', uselist=False)

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "entry",
            "id": self.entry_id
        }

    def _get_links(self, rel_name):
        url_prefix = current_app.config["API_URL_PREFIX"]
        return {
            "links": {
                "self": "%s/entries/%s/relationships/%s" % (url_prefix, self.entry_id, rel_name),
                "related": "%s/entries/%s/%s" % (url_prefix, self.entry_id, rel_name)
            }
        }

    @property
    def links_insee_commune(self):
        return self._get_links("insee-commune")

    @property
    def links_localization_insee_commune(self):
        return self._get_links("localization-insee-commune")

    @property
    def links_localization_entry(self):
        return self._get_links("localization-entry")

    @property
    def links_alt_orths(self):
        return self._get_links("alt-orths")

    @property
    def links_old_orths(self):
        return self._get_links("old-orths")

    @property
    def resource(self):
        """Make a JSONAPI resource object describing what is a dictionnary entry

        A dictionnary entry is made of:
        attributes:
            orth:
            country:
            dpt:
            def:
            localization-certainty (optional):
        relationships:


        Returns
        -------
            A dict describing the corresponding JSONAPI resource object
        """
        url_prefix = current_app.config["API_URL_PREFIX"]
        return {
            **self.resource_identifier,
            "attributes": {
                "orth": self.orth,
                "country": self.country,
                "dpt": self.dpt,
                "def": self.def_col,
                "localization-certainty": self.localization_certainty
            },
            "relationships": {
                "insee-commune": {
                    **self.links_insee_commune,
                    "data": None if self.insee is None else self.insee.resource_identifier
                },
                "localization-insee-commune": {
                    **self.links_localization_insee_commune,
                    "data": None if self.localization_insee is None else self.localization_insee.resource_identifier
                },
                "localization-entry": {
                    **self.links_localization_entry,
                    "data": None if self.localization_entry is None else self.localization_entry.resource_identifier
                },
                "alt-orths": {
                    **self.links_alt_orths,
                    "data": [] if self.alt_orths is None else [_as.resource_identifier for _as in self.alt_orths]
                },
                "old-orths": {
                    **self.links_old_orths,
                    "data": [] if self.old_orths is None else [_os.resource_identifier for _os in self.old_orths]
                },
            },
            "meta": {},
            "links": {
                "self": "%s/entries/%s" % (url_prefix, self.entry_id)
            }
        }


class AltOrth(db.Model):
    """ """
    __tablename__ = 'alt_orth'
    entry_id = db.Column(db.String(10), db.ForeignKey(Entry.entry_id), primary_key=True)
    alt_orth = db.Column(db.String(200), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('alt_orths'))

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "alt-orth",
            "id": self.entry_id
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "alt_orth": self.alt_orth
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


class Keywords(db.Model):
    """ """
    __tablename__ = 'keywords'
    entry_id = db.Column(db.String(10), db.ForeignKey('entry.entry_id'), primary_key=True)
    term = db.Column(db.String(400), primary_key=True)

    entry = db.relationship(Entry, backref=db.backref('keywords'))

    @property
    def unique_id(self):
        """ """
        return "%s_%s" % (self.entry_id, self.term)

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "keyword",
            "id": self.unique_id
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "term": self.term
            },
            "relationships": {
                "entry": {
                    "links": {
                        "self": "/keywords/%s/relationships/entry" % self.unique_id,
                        "related": "/keywords/%s/entry" % self.unique_id
                    },
                    "data": self.entry.resource_identifier
                }
            },
            "meta": {},
            "links": {
                "self": "/keywords/%s" % self.unique_id
            }
        }


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

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "old-orth",
            "id": self.id
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                "orth": self.old_orth,
                "date-rich": self.date_rich,
                "date-nude": self.date_nude,
                "reference-rich": self.date_rich,
                "reference-nude": self.date_nude
            },
            "relationships": {
                "entry": {
                    "links": {
                        "self": "/old-orths/%s/relationships/entry" % self.id,
                        "related": "/old-orths/%s/entry" % self.id
                    },
                    "data": self.entry.resource_identifier
                },
                "old-orths": {
                    "links": {
                        "self": "/old-orths/%s/relationships/old-orths" % self.id,
                        "related": "/old-orths/%s/old-orths" % self.id
                    },
                    "data": [oo.resource_identifier for oo in self.entry.old_orths]
                }
            },
            "meta": {},
            "links": {
                "self": "/old-orths/%s" % self.id
            }
        }


class InseeCommune(db.Model):
    """ """
    __tablename__ = 'insee_commune'
    insee_id = db.Column(db.String(5), primary_key=True)
    REG_id = db.Column(db.String(6), db.ForeignKey('insee_ref.id'), nullable=False)
    DEP_id = db.Column(db.String(7), db.ForeignKey('insee_ref.id'), nullable=False)
    AR_id = db.Column(db.String(8), db.ForeignKey('insee_ref.id'))
    CT_id = db.Column(db.String(9))
    NCCENR = db.Column(db.String(70), nullable=False)
    ARTMIN = db.Column(db.String(10))
    longlat = db.Column(db.String(100))

    reg = db.relationship('InseeRef', backref=db.backref('reg'),
                          primaryjoin="InseeCommune.REG_id==InseeRef.id")
    dep = db.relationship('InseeRef', backref=db.backref('dep'),
                          primaryjoin="InseeCommune.DEP_id==InseeRef.id")
    ar = db.relationship('InseeRef', backref=db.backref('ar'),
                         primaryjoin="InseeCommune.AR_id==InseeRef.id")

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "insee-commune",
            "id": self.insee_id
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'CT_id': self.CT_id,
                'NCCENR': self.NCCENR,
                'ARTMIN': self.ARTMIN,
                'longlat': self.longlat
            },
            "relationships": {
                "reg": {
                    "links": {
                        "self": "/insee-communes/%s/relationships/reg" % self.insee_id,
                        "related": "/insee-communes/%s/reg" % self.insee_id
                    },
                    "data": self.reg.resource_identifier
                },
                "dep": {
                    "links": {
                        "self": "/insee-communes/%s/relationships/dep" % self.insee_id,
                        "related": "/insee-communes/%s/dep" % self.insee_id
                    },
                    "data": self.dep.resource_identifier
                },
                "ar": {
                    "links": {
                        "self": "/insee-communes/%s/relationships/ar" % self.insee_id,
                        "related": "/insee-communes/%s/ar" % self.insee_id
                    },
                    "data": self.dep.resource_identifier
                }
            },
            "meta": {},
            "links": {
                "self": "/insee-communes/%s" % self.insee_id
            }
        }


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

    @property
    def resource_identifier(self):
        """
        Returns
        -------
            A JSONAPI resource object identifier
        """
        return {
            "type": "insee-ref",
            "id": self.id
        }

    @property
    def resource(self):
        """ """
        return {
            **self.resource_identifier,
            "attributes": {
                'ref-type': self.type,
                'insee': self.insee,
                'level': self.level,
                'label': self.label
            },
            "relationships": {
                "parent": {
                    "links": {
                        "self": "/insee-refs/%s/relationships/parent" % self.id,
                        "related": "/insee-refs/%s/parent" % self.id
                    },
                    "data": None if self.parent is None else self.parent.resource_identifier
                },
                "children": {
                    "links": {
                        "self": "/insee-refs/%s/relationships/children" % self.id,
                        "related": "/insee-refs/%s/children" % self.id
                    },
                    "data": [] if self.children is None else [c.resource_identifier for c in self.children]
                }
            },
            "meta": {},
            "links": {
                "self": "/insee-refs/%s" % self.id
            }
        }
