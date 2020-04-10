import sys

sys.path.append('../..')

from app import create_app, db
from app.models import InseeCommune

filename = '../communes_linking.tsv'

if __name__ == "__main__":
    # python communes-linking.py dev
    try:
        app = create_app(sys.argv[1])
    except Exception as e:
        raise e

    with app.app_context():

        with open(filename) as f:
            # skip the header
            f.readline()
            rejected = 0
            for l, line in enumerate(f.readlines()):
                insee, geoname, wikidata, wikipedia, databnf, viaf, siaf = [i.strip() for i in line.split("\t")]

                if len(insee) == 0:
                    print("Cannot parse line %s" % (l+2))
                    rejected += 1
                else:
                    co = InseeCommune.query.filter(InseeCommune.id == insee).first()
                    if co is None:
                        print("Insee code '%s' (l. %s) not found in database" % (insee, l+2))
                        rejected += 1
                    else:
                        if len(geoname) > 0:
                            co.geoname_id = geoname.strip()
                        if len(wikidata) > 0:
                            co.wikidata_item_id = wikidata.strip()
                        if len(wikipedia) > 0:
                            co.wikipedia_url = wikipedia.strip()
                        if len(databnf) > 0:
                            co.databnf_ark = databnf.strip()
                        if len(viaf) > 0:
                            co.viaf_id = viaf.strip()
                        if len(siaf) >0:
                            co.siaf_id = siaf.strip()

                        db.session.add(co)
            try:
                db.session.commit()
            except Exception as e:
                print(str(e))
                db.session.rollback()

            print("rejected: %s  passed: %s" %(rejected, l+2))
