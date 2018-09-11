import json
from flask import Response

from app import api_bp, db
from app.models import Entry, InseeRef, InseeCommune, AltOrth


@api_bp.route('/api/<api_version>/init')
def api_init(api_version):

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

    alt_orth1 = AltOrth(entry_id=e2.entry_id, label="Commune numéro une")
    alt_orth2 = AltOrth(entry_id=e2.entry_id, label="Commune n°1")
    db.session.add(alt_orth1)
    db.session.add(alt_orth2)
    db.session.commit()

    return Response("init ok")


@api_bp.route('/api/<api_version>/entries/<entry_id>')
def api_entries(api_version, entry_id):
    e = Entry.query.filter(Entry.entry_id == entry_id).first()
    resource = None if e is None else e.resource
    return Response(
            json.dumps(resource, indent=2, ensure_ascii=False),
            content_type="application/vnd.api+json; charset=utf-8",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@api_bp.route('/api/<api_version>/entries/<entry_id>/insee')
def api_entries_insee(api_version, entry_id):
    e = Entry.query.filter(Entry.entry_id == entry_id).first()
    resource = None if e is None or e.insee is None else e.insee.resource
    return Response(
            json.dumps(resource, indent=2, ensure_ascii=False),
            content_type="application/vnd.api+json; charset=utf-8",
            headers={"Access-Control-Allow-Origin": "*"}
        )