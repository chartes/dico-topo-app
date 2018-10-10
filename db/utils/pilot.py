import sqlite3
import insee
import dt2db
import sys

# DT_with_insee = ["DT01", "DT02", "DT05", "DT10", "DT14", "DT15", "DT18", "DT21", "DT24", "DT26", "DT27", "DT30", "DT42", "DT43", "DT51", "DT52", "DT54", "DT55", "DT56", "DT57", "DT58", "DT65", "DT68", "DT71", "DT72", "DT76", "DT77", "DT79", "DT80", "DT88", "DT89"]
# DT_without_insee = ["DT28", "DT34", "DT62", "DT64"]
# bazar_todo = ["DT68", "DT89"]

db_path = '../dicotopo-dev.sqlite'
dt_id = 'DT89'
dpt_code = dt_id[-2:]

db = sqlite3.connect(db_path)
cursor = db.cursor()
cursor.execute('PRAGMA foreign_keys=ON')

print("%s processing\n===============" % dt_id)

# 0. création du modèle avec flask_app.py
# 1. insertion et enrichissement (hiérarchie adm, longlat) des infos référentiel insee
# insee.insert_insee_ref(db, cursor)
# insee.insert_insee_commune(db, cursor)
# insee.update_insee_ref(db, cursor)
# insee.insert_longlat(db, cursor, 'tsv')

# 2. création et insertion des entry (une entrée du DT), altorth (aorthographic form alternative)  et keywords (feature types)
dt2db.insert_placename_values(db, cursor, dt_id)
dt2db.update_localization_placename_id(db, cursor, dpt_code)
# 3. insertion des formes anciennes
dt2db.insert_placename_old_label(db, cursor, dt_id)

db.close()

