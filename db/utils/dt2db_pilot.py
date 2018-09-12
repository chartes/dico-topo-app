import sqlite3
import insee
import entry
import ref

db_path = '../dicotopo-dev.sqlite'
dt_id = 'DT02'

db = sqlite3.connect(db_path)
cursor = db.cursor()
cursor.execute('PRAGMA foreign_keys=ON')

# 0. création du modèle avec flask_app.py
# 1. insertion et enrichissement (hiérarchie adm, longlat) des infos référentiel insee
# print('création des tables de référence insee')
# insee.insert_insee_ref(db, cursor)
# insee.insert_insee_commune(db, cursor)
# insee.update_insee_ref(db, cursor)
# # enrichissement: ajout des coordonnées (method='api|tsv')
# insee.insert_longlat(db, cursor, 'tsv')


# 2. création et insertion des entry (une entrée du DT), altorth (aorthographic form alternative)  et keywords (feature types)
# insertion des entries
entry.insert_entry_values(db, cursor, dt_id)
entry.fill_localisation_entry_id(db, cursor)

# 3. insertion des refs
ref.insert_ref_values(db, cursor, dt_id)
db.close()

