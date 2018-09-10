import sqlite3
import insee

db = sqlite3.connect('../dicotopo-dev.sqlite')
cursor = db.cursor()

print('création des tables de référence insee')
# insee.create_insee_ref(db, cursor)
# insee.insert_insee_ref(db, cursor)
# insee.create_insee_communes(db, cursor)
# insee.insert_insee_communes(db, cursor)
insee.update_insee_ref(db, cursor)
# insee.insert_longlat(db, cursor, 'tsv')

