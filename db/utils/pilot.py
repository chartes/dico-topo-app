import sqlite3
import insee
import dt2db
import sys


# INSEE COG year (Code officiel géographique)
# Paramétrage de l’année du COG à charger en base
# 2011: https://www.insee.fr/fr/information/2560625, `./insee/2011/`
# 2018: https://www.insee.fr/fr/information/3363419, `./insee/2018/`
COG_year = "2011"

# DT68 et DT89 plantent, revoir
# DT_without_insee = ["DT28", "DT34", "DT62", "DT64"]
DT_with_insee = ["DT01", "DT02", "DT05", "DT10", "DT14", "DT15", "DT18", "DT21", "DT24", "DT26", "DT27", "DT30", "DT42", "DT43", "DT51", "DT52", "DT54", "DT55", "DT56", "DT57", "DT58", "DT65", "DT71", "DT72", "DT76", "DT77", "DT79", "DT80", "DT88"]
DT_with_insee = ["DT02"]

db_path = '../dicotopo.dev.sqlite'

for dt_id in DT_with_insee:
    dpt_code = dt_id[-2:]

    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')

    print("%s processing\n===============" % dt_id)

    # 0. création du modèle avec flask_app.py
    # 1. insertion et enrichissement (hiérarchie adm, longlat) des infos référentiel insee
    insee.insert_insee_ref(db, COG_year, cursor)
    insee.insert_insee_commune(db, COG_year, cursor)
    insee.insert_longlat(db, cursor, 'tsv')

    # si on charge la liste de toutes les communes depuis 1943 (`france{AAAA}.txt`), appeler insee.update_insee_ref()
    # insee.update_insee_ref(db, cursor)


    # 2. création et insertion des entry (une entrée du qqDT), altorth (aorthographic form alternative)  et keywords (feature types)
    # dt2db.insert_place_values(db, cursor, dt_id)
    # dt2db.update_localization_place_id(db, cursor, dpt_code)
    # 3. insertion des formes anciennes
    dt2db.insert_place_old_label(db, cursor, dt_id)

db.close()

