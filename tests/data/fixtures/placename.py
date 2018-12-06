
from app.models import InseeRef, InseeCommune, Placename, PlacenameAltLabel, PlacenameOldLabel


def load_fixtures(db):
    # INSEE REF
    ref1 = InseeRef(id="ref1", type="type1", insee_code="ABC", level="1", label="this is ref1")
    ref2 = InseeRef(id="ref2", type="type2", insee_code="ABC", level="1", label="this is ref2", parent_id=ref1.id)
    ref3 = InseeRef(id="ref3", type="type3", insee_code="ABC", level="1", label="this is ref3", parent_id=ref2.id)
    db.session.add(ref1)
    db.session.add(ref2)
    db.session.add(ref3)
    db.session.commit()

    # INSEE COMMUNE
    commune1 = InseeCommune(id="Commune1", REG_id=ref1.id, DEP_id=ref2.id, AR_id=ref3.id, NCCENR="NCCENR_TEST")
    commune2 = InseeCommune(id="Commune2", REG_id=ref1.id, DEP_id=ref2.id, AR_id=ref3.id, NCCENR="NCCENR_TEST")
    db.session.add(commune1)
    db.session.add(commune2)
    db.session.commit()

    # PLACENAME
    e1 = Placename(id="id1", label="Commune Un", country="FR", dpt="57",
                   commune_insee_code=commune1.id,
                   localization_commune_insee_code=commune2.id,
                   localization_certainty="low",
                   desc="this is a def col",
                   num_start_page=1,
                   comment="this is a comment")
    db.session.add(e1)
    db.session.commit()

    e2 = Placename(id="id2", label="Commune Deux", country="FR", dpt="88",
                   commune_insee_code=commune2.id,
                   localization_commune_insee_code=commune2.id,
                   localization_placename_id=e1.id,
                   localization_certainty="high",
                   desc="this is a def col",
                   num_start_page=2,
                   comment="this is another comment")

    db.session.add(e2)
    db.session.commit()

    e3 = Placename(id="id3", label="Commune Trois", country="FR", dpt="03",
                   commune_insee_code=None,
                   localization_commune_insee_code=None,
                   localization_placename_id=None,
                   localization_certainty=None,
                   desc=None,
                   num_start_page=None,
                   comment=None)

    db.session.add(e3)
    db.session.commit()

    placename_alt_label1 = PlacenameAltLabel(placename_id=e2.id, label="Commune numéro une")
    placename_alt_label2 = PlacenameAltLabel(placename_id=e2.id, label="Commune n°1")
    db.session.add(placename_alt_label1)
    db.session.add(placename_alt_label2)
    db.session.commit()

    old_label1 = PlacenameOldLabel(old_label_id='PLACENAME1_OLD_1', placename_id=e1.id, rich_label="Cmune Un")
    old_label2 = PlacenameOldLabel(old_label_id='PLACENAME1_OLD_2', placename_id=e1.id, rich_label="Cmn Un")
    old_label3 = PlacenameOldLabel(old_label_id='PLACENAME1_OLD_3', placename_id=e1.id, rich_label="Comm Un")
    db.session.add(old_label1)
    db.session.add(old_label2)
    db.session.add(old_label3)
    db.session.commit()
