import json
from flask import Response

from app import api_bp, db
from app.api.response_factory import JSONAPIResponseFactory
from app.models import Entry, InseeRef, InseeCommune, AltOrth, OldOrth


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

    old_orth1 = OldOrth(old_orth_id='ENTRY1_OLD_1', entry_id=e1.entry_id, old_orth="Cmune Un")
    old_orth2 = OldOrth(old_orth_id='ENTRY1_OLD_2', entry_id=e1.entry_id, old_orth="Cmn Un")
    old_orth3 = OldOrth(old_orth_id='ENTRY1_OLD_3', entry_id=e1.entry_id, old_orth="Comm Un")
    db.session.add(old_orth1)
    db.session.add(old_orth2)
    db.session.add(old_orth3)
    db.session.commit()

    return Response("init ok")


def get_entry(entry_id):
    e = Entry.query.filter(Entry.entry_id == entry_id).first()
    if e is None:
        kwargs = {"status": 404}
        errors = [{"status": 404, "title": "entry %s does not exist" % entry_id}]
    else:
        kwargs = {}
        errors = []
    return e, kwargs, errors


@api_bp.route('/api/<api_version>/entries/<entry_id>')
def api_get_entry(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        return JSONAPIResponseFactory.make_data_response(e.resource)


@api_bp.route('/api/<api_version>/entries/<entry_id>/relationships/insee-commune')
def api_get_entry_relationships_insee_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        data = {
            **e.links_insee_commune,
            "data": e.insee.resource_identifier
        }
        return JSONAPIResponseFactory.make_response(data, **kwargs)


@api_bp.route('/api/<api_version>/entries/<entry_id>/insee-commune')
def api_get_entry_insee_commune(api_version, entry_id):
    e, kwargs, errors = get_entry(entry_id)
    if e is None:
        return JSONAPIResponseFactory.make_errors_response(errors, **kwargs)
    else:
        return JSONAPIResponseFactory.make_data_response(e.insee.resource)

