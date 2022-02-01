import sqlite3
import insee
import dt2db
import sys
import time

'''
Insertion de nouveaux DT en base.
Procédure:
    1. Avant insertion : calcul de nouveaux ids à injecter dans la source XML
    2. Insertion en base
'''

start_time = time.time()

db_path = '../dicotopo.dev.sqlite'
db = sqlite3.connect(db_path)
cursor = db.cursor()
cursor.execute('PRAGMA foreign_keys=ON')


# 1. Avant insertion : calcul de nouveaux ids à injecter dans la source XML
dt2db.new_ids_generator_tsv(db, cursor, 'DT68')
exit()

# création du user
u1 = {"id": 1, "username": "delisle", "is_admin": 1}
cursor.execute("INSERT OR REPLACE INTO user (id, username, is_admin) VALUES (?, ?, ?);",
               (u1["id"], u1["username"], u1["is_admin"]))
db.commit()

# 1. insertion et enrichissement (hiérarchie adm, longlat) des infos référentiel insee
# INSEE COG year (Code officiel géographique)
# Paramétrage de l’année du COG à charger en base
# 2011: https://www.insee.fr/fr/information/2560625, `./insee/2011/`
# 2018: https://www.insee.fr/fr/information/3363419, `./insee/2018/`

# Tables de référence
"""
COG_year = "2011"
insee.insert_insee_ref(db, COG_year, cursor)
insee.insert_insee_commune(db, COG_year, cursor)
insee.insert_longlat(db, cursor, 'tsv')
"""

# penser ensuite aux liages: `utils % python communes-linking.py dev
# si on charge la liste de toutes les communes depuis 1943 (`france{AAAA}.txt`), appeler insee.update_insee_ref()
# insee.update_insee_ref(db, cursor)

DT_with_insee = [
    "DT01", "DT02", "DT05", "DT07", "DT10",
    "DT11", "DT14", "DT15", "DT18", "DT21",
    "DT23", "DT24", "DT26", "DT27", "DT28",
    "DT30", "DT34", "DT36", "DT41", "DT42",
    "DT43", "DT44", "DT51", "DT52", "DT54",
    "DT55", "DT56", "DT57", "DT58", "DT60",
    "DT62", "DT64", "DT68", "DT71", "DT72",
    "DT76", "DT77", "DT79", "DT80", "DT86",
    "DT88", "DT89"]

DT_with_insee = ["DT68"]

for dt_id in DT_with_insee:
    dpt_code = dt_id[-2:]
    print("===%s processing===" % dt_id)
    # bibl, place, place_alt_label, place_comment, place_description, place_feature_type
    dt2db.insert_place_values(db, cursor, dt_id, u1["id"])
    # place_old_labels
    dt2db.insert_place_old_label(db, cursor, dt_id)
    # debug.get_old_label(db, cursor, dt_id)

db.close()
print("--- %s seconds ---" % (time.time() - start_time))
