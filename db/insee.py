import csv
import requests

"""
import des données de l’INSEE, pour
    * tester intégrité des données DT
    * rétablir les hiérarchies administratives
    * préparer les liages (OSM, wikidata, etc.)

Sources
    * Liste des régions: https://www.insee.fr/fr/information/3363419#titre-bloc-26
    * Liste des départements: https://www.insee.fr/fr/information/3363419#titre-bloc-23
    * Liste des arrondissements: https://www.insee.fr/fr/information/3363419#titre-bloc-19
    * Liste des cantons: https://www.insee.fr/fr/information/3363419#titre-bloc-15

Problème: on a la table de référence insee (insee_ref), mais sans le parent pour les Cantons
on doit donc procéder en 2 passes pour cette table
1.a. chargement de la table insee_ref (mais sans parent_id pour les cantons)
1.b. chargement de la table insee_communes avec les tests adhoc
2. UPDATE de insee_ref (parent_id des cantons) grâce à la table insee_communes
 
"""

# Liste des communes. On conserve les étiquettes de l’INSEE: https://www.insee.fr/fr/information/3363419#titre-bloc-7

# On ne valide pas les cantons: problème de cantons antérieurs à 2018
def create_insee_communes(db, cursor):
    sql = """CREATE TABLE IF NOT EXISTS insee_communes (
      insee_id  CHAR(5)     NOT NULL,
      REG_id    CHAR(6)     NOT NULL,
      DEP_id    VARCHAR(7)  NOT NULL,
      AR_id     VARCHAR(8),
      CT_id     VARCHAR(9),   
      NCCENR    VARCHAR(70) NOT NULL,
      ARTMIN    VARCHAR(10),
      longlat   VARCHAR(100),
      PRIMARY KEY (insee_id),
      FOREIGN KEY (REG_id)  REFERENCES insee_ref(id),
      FOREIGN KEY (DEP_id)  REFERENCES insee_ref(id),
      FOREIGN KEY (AR_id)   REFERENCES insee_ref(id)
    );
    """
    cursor.execute(sql)
    db.commit()


def create_insee_ref(db, cursor):
    sql = """CREATE TABLE IF NOT EXISTS insee_ref (
          id        VARCHAR(10) NOT NULL,
          type      VARCHAR(4) NOT NULL,
          insee     VARCHAR(3) NOT NULL,
          parent_id VARCHAR(10),
          level     INT(1) NOT NULL,
          label     VARCHAR(50),
          PRIMARY KEY (id)
        );
        """
    cursor.execute(sql)
    db.commit()


def insert_insee_communes(db, cursor):
    with open('insee/France2018.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        insee_id_list = []
        for row in reader:
            insee_COM = str(row['DEP']) + str(row['COM'])
            # 278 codes insee ont été réattribués de 3 à 13 fois… On ne conserve que le premier
            # NB: utile que sur France2018.txt
            if insee_COM in insee_id_list:
                continue
            insee_id_list.append(insee_COM)
            # des communes dans un arrondissement (AR) mais hors canton (CT), et
            # des communes dans un CT mais hors AR
            AR_insee = row['AR'] if row['AR'] else None
            AR_id    = 'AR_'+row['DEP']+'-'+AR_insee if AR_insee else None
            CT_insee = row['CT'] if row['CT'] else None
            CT_id    = 'CT_' + row['DEP'] + '-' + CT_insee if CT_insee else None
            # cas des communes localisées dans l’ancien département corse (20)
            # TODO: corriger le référentiel ?
            REG_id   = 'REG_94' if row['DEP'] == '20' else 'REG_'+row['REG']
            cursor.execute("INSERT INTO insee_communes"
                           "(insee_id, REG_id, DEP_id, AR_id, CT_id, NCCENR, ARTMIN) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                           (insee_COM, REG_id, 'DEP_'+row['DEP'], AR_id, CT_id, row['NCCENR'], row['ARTMIN']))
            db.commit()


def insert_insee_ref(db, cursor):
    with open('insee/reg2018.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee, parent_id, level, label) VALUES(%s, %s, %s, %s, %s, %s)",
                ('REG_'+row['REGION'], 'REG', row['REGION'], 'FR', '2', row['NCCENR']))
            db.commit()
    with open('insee/depts2018.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee, parent_id, level, label) VALUES(%s, %s, %s, %s, %s, %s)",
                ('DEP_'+row['DEP'], 'DEP', row['DEP'], 'REG_'+row['REGION'], '3', row['NCCENR']))
            db.commit()
    with open('insee/arrond2018.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee, parent_id, level, label) VALUES(%s, %s, %s, %s, %s, %s)",
                ('AR_' + row['DEP'] + '-' + row['AR'], 'AR', row['AR'], 'DEP_' + row['DEP'], '4', row['NCCENR']))
            db.commit()
    # NB: les cantons ne dépendent pas toujours d’un arrondissement ! -> parent n’est pas obligatoire
    # todo: si les cantons ne dépendent pas d‘un arrondissement, rattacher au DEP (en parent_id) ?
    with open('insee/canton2018.txt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            id = 'CT_' + row['DEP'] + '-' + row['CANTON']
             # parent_id = ("SELECT DISTINCT AR_id FROM dicotopo.insee_communes WHERE CT_id = '%s'" % id)
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee, parent_id, level, label) VALUES(%s, %s, %s, %s, %s, %s)",
                (id, 'CT', row['CANTON'], None, '5', row['NCCENR']))
            db.commit()
    # EXCEPTIONS (à reprendre)
    cursor.execute("INSERT INTO insee_ref (id, type, insee, parent_id, level, label)"
                   "VALUES('DEP_20', 'DEP', '20', 'REG_94', '3', 'Corse')")
    db.commit()
    cursor.execute("INSERT INTO insee_ref (id, type, insee, parent_id, level, label)"
                   "VALUES('FR', 'PAYS', 'FR', NULL, '1', 'France')")
    db.commit()


"""
On récupère l’id de l’AR parent du CT dans la table insee_commune. Problème :
    * 17 Communes dépendent d’un CT mais pas d’un AR dans insee_communes (des cantons qui ne dépendent pas d’un arrondissement)
    * 255 CT restent sans AR parent après enreichissement (sans doute des CT listés in insee_ref, absent de insee_commune)
TODO: comment régler cette absence de parent ?
    1. On créer un AR avec l’id unspecified_AR ?
    2. On considère que le CT est rattaché au DEP ? (sont parent_id devient celui d’un DEP et son level passe de 5 à 4)
    Problème, 2 peut-être faux (information simplement manquante dans insee_commune)
"""
def update_insee_ref(db, cursor):
    # get CT parent_id in table insee_communes
    cursor.execute("SELECT id FROM insee_ref WHERE type= 'CT'")
    for canton in cursor:
        ct_id = canton[0]
        cursor.execute(("SELECT DISTINCT AR_id FROM dicotopo.insee_communes WHERE CT_id = '%s'" % ct_id))
        parent_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        if parent_id is None:
            continue
        else:
            cursor.execute(("UPDATE insee_ref SET parent_id = '%s' WHERE id = '%s'" % (parent_id, ct_id)))
            db.commit()


def insert_longlat(db, cursor, method):
    # on ne dispose pas des coords, on va les chercher sur https://api.gouv.fr/api/api-geo.html
    if method == 'api':
        cursor.execute("SELECT insee_id FROM insee_communes")
        for insee_id in cursor:
            insee_id = insee_id[0]
            longlat = get_longlat(insee_id)
            if longlat is not None:
                print('insert de ' + insee_id + '    ' + longlat)
                cursor.execute(("UPDATE insee_communes SET longlat = '%s' WHERE insee_id = '%s'" % (longlat, insee_id)))
                db.commit()
            else:
                continue
    # on dispose du mapping insee_id/coords in longlat-by-insee_id.tsv
    elif method == 'tsv':
        with open('insee/longlat-by-insee_id.tsv', 'r') as f:
            data = csv.reader(f, delimiter="\t")
            for row in data:
                insee_id = row[0]
                longlat = row[1]
                print('insert de ' + insee_id + '    ' + longlat)
                cursor.execute(("UPDATE insee_communes SET longlat = '%s' WHERE insee_id = '%s'" % (longlat, insee_id)))
                db.commit()
    else:
        return


def get_longlat(insee_id):
    getGeo = 'https://geo.api.gouv.fr/communes/%s?fields=centre&format=json&geometry=centre' % insee_id
    r = requests.get(getGeo)
    # print(insee_id + ' is ' + str(r.status_code))
    if r.status_code == 404:
        return
    else:
        if requests.get(getGeo).json()["centre"]:
            longlat = r.json()["centre"]["coordinates"]
            longlat = '(%s, %s)' % (longlat[0], longlat[1])
            return longlat
        else:
            return

