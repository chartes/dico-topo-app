
from app.models import InseeRef, InseeCommune, Entry, AltOrth, OldOrth


def load_fixtures(db):
    # INSEE REF
    ref1 = InseeRef(id="ref1", type="type1", insee="ABC", level="1", label="this is ref1")
    ref2 = InseeRef(id="ref2", type="type2", insee="ABC", level="1", label="this is ref2", parent_id=ref1.id)
    ref3 = InseeRef(id="ref3", type="type3", insee="ABC", level="1", label="this is ref3", parent_id=ref2.id)
    db.session.add(ref1)
    db.session.add(ref2)
    db.session.add(ref3)
    db.session.commit()

    # INSEE COMMUNE
    commune1 = InseeCommune(insee_id="Commune1", REG_id=ref1.id, DEP_id=ref2.id, AR_id=ref3.id, NCCENR="NCCENR_TEST")
    commune2 = InseeCommune(insee_id="Commune2", REG_id=ref1.id, DEP_id=ref2.id, AR_id=ref3.id, NCCENR="NCCENR_TEST")
    db.session.add(commune1)
    db.session.add(commune2)
    db.session.commit()

    # ENTRY
    e1 = Entry(entry_id="id1", orth="Commune Un", country="FR", dpt="57",
               insee_id=commune1.insee_id,
               localization_insee_id=commune2.insee_id,
               localization_certainty="low",
               def_col="this is a def col")
    db.session.add(e1)
    db.session.commit()

    e2 = Entry(entry_id="id2", orth="Commune Deux", country="FR", dpt="88",
               insee_id=commune2.insee_id,
               localization_insee_id=commune2.insee_id,
               localization_entry_id=e1.entry_id,
               localization_certainty="high",
               def_col="this is a def col")

    db.session.add(e2)
    db.session.commit()

    e3 = Entry(entry_id="id3", orth="Commune Trois", country="FR", dpt="03",
               insee_id=None,
               localization_insee_id=None,
               localization_entry_id=None,
               localization_certainty=None,
               def_col=None)

    db.session.add(e3)
    db.session.commit()

    alt_orth1 = AltOrth(entry_id=e2.entry_id, alt_orth="Commune numéro une")
    alt_orth2 = AltOrth(entry_id=e2.entry_id, alt_orth="Commune n°1")
    db.session.add(alt_orth1)
    db.session.add(alt_orth2)
    db.session.commit()

    old_orth1 = OldOrth(old_orth_id='ENTRY1_OLD_1', entry_id=e1.entry_id, old_orth="Cmune Un")
    old_orth2 = OldOrth(old_orth_id='ENTRY1_OLD_2', entry_id=e1.entry_id, old_orth="Cmn Un")
    old_orth3 = OldOrth(old_orth_id='ENTRY1_OLD_3', entry_id=e1.entry_id, old_orth="Comm Un")
    db.session.add(old_orth1)
    db.session.add(old_orth2)
    db.session.add(old_orth3)
    db.session.commit()