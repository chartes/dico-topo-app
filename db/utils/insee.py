import sqlite3
import csv
import requests

"""
import en base des données du Code officiel géographique (COG) de l’INSEE utiles :
    * aux tests d’intégrité des données DT;
    * à l’affichage des hiérarchies administratives (Département > Canton > Commune);
    * à la récupération des coordonnées géographiques des communes;
    * au liage (OSM, wikidata, etc.) des entités.

Sources COG INSEE : https://www.insee.fr/fr/information/2560452

Le choix a été fait de retenir le COG 2011 pour le pilotage de l’application.
    * Liste des régions: https://www.insee.fr/fr/information/2560625#titre-bloc-29
    * Liste des départements: https://www.insee.fr/fr/information/2560625#titre-bloc-26
    * Liste des arrondissements: https://www.insee.fr/fr/information/2560625#titre-bloc-22
    * Liste des cantons: https://www.insee.fr/fr/information/2560625#titre-bloc-19
    * Liste des communes: https://www.insee.fr/fr/information/2560625#titre-bloc-7
Ces ressources sont disponibles dans `./insee/2011/`

Il est possible de générer la base de référence, en utilsant le COG d’une autre année:
    * paramétrer COG_year
    * enregister les données dans `./insee/{YEAR}/`

NB1. Les liages (../communes-linking.tsv) et coordonnées (../commune_long_lat.tsv) disponibles le sont pour
l’intégralité des communes listées dans le COG 2018 des communes existantes depuis 1943:
https://www.insee.fr/fr/information/3363419#titre-bloc-3
Ces données peuvent/doivent être mises à jour indépendemment du rechargement en base du COG INSEE.

NB2. Pour mémoire, difficulté avec le COG2018 
Le COG INSEE 2018 des cantons ne spécifie pas d’arrondissement de rattachement (pour les cantons).


Problème: on a la table de référence insee (insee_ref), mais sans le parent pour les Cantons
on doit donc procéder en 2 passes pour cette table
1.a. chargement de la table insee_ref (mais sans parent_id pour les cantons)
1.b. chargement de la table insee_commune avec les tests adhoc
2. UPDATE de insee_ref (parent_id des cantons) grâce à la table insee_commune
 
"""

def insert_insee_ref(db, COG_year, cursor):
    """ """
    print("BUILD INSEE REF: fill insee_ref\n===============================")
    cursor.execute("INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                   "VALUES('FR', 'PAYS', 'FR', NULL, '1', 'France')")
    db.commit()
    with open('insee/{0}/reg{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                "VALUES(?, ?, ?, ?, ?, ?)",
                ('REG_'+row['REGION'], 'REG', row['REGION'], 'FR', '2', row['NCCENR']))
            db.commit()
    with open('insee/{0}/depts{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                "VALUES(?, ?, ?, ?, ?, ?)",
                ('DEP_'+row['DEP'], 'DEP', row['DEP'], 'REG_'+row['REGION'], '3', row['NCCENR']))
            db.commit()
    with open('insee/{0}/arrond{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            cursor.execute(
                "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                "VALUES(?, ?, ?, ?, ?, ?)",
                ('AR_' + row['DEP'] + '-' + row['AR'], 'AR', row['AR'], 'DEP_' + row['DEP'], '4', row['NCCENR']))
            db.commit()
    with open('insee/{0}/canton{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        # canton2018.txt, ne renseigne pas l’arrondissement d’appartenance -> procédure plus complexe
        # voir update_insee_ref()
        if COG_year == '2018':
            for row in reader:
                id = 'CT_' + row['DEP'] + '-' + row['CANTON']
                cursor.execute(
                    "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                    "VALUES(?, ?, ?, ?, ?, ?)",
                    (id, 'CT', row['CANTON'], None, '5', row['NCCENR']))
                db.commit()
        # A priori. Vérifier que la donnée (parent_id) est bien disponible pour toutes les autres années du COG.
        else:
            for row in reader:
                id = 'CT_' + row['DEP'] + '-' + row['CANTON']
                parent_id = 'AR_' + row['DEP'] + '-' + row['AR']
                cursor.execute(
                    "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                    "VALUES(?, ?, ?, ?, ?, ?)",
                    (id, 'CT', row['CANTON'], parent_id, '5', row['NCCENR']))
                db.commit()
    # liste des cantons "non précisés" (type CTNP) pour les communes découpées en canton
    with open('insee/{0}/comsimp{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            # https://www.insee.fr/fr/information/2560628#ct
            if 84 <= int(row['CT']) <= 99:
                id = 'CT_' + row['DEP'] + '-' + row['CT']
                parent_id = 'AR_' + row['DEP'] + '-' + row['AR']
                label = row['NCCENR'] + '-NP'
                #print(id + ' > ' + parent_id + ' > ' + label)
                cursor.execute(
                    "INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                    "VALUES(?, ?, ?, ?, ?, ?)",
                    (id, 'CTNP', row['CT'], parent_id, '5', label))
                db.commit()

    # EXCEPTIONS (à reprendre)
    # DEP_20, ancien département de la Corse, pour les anciennes communes (vieux codes communes)
    cursor.execute("INSERT INTO insee_ref (id, type, insee_code, parent_id, level, label)"
                   "VALUES('DEP_20', 'DEP', '20', 'REG_94', '3', 'Corse')")
    db.commit()


# Liste uniquement des communes existantes au 1er janvier (comsimp{AAAA}.txt).
# On conserve les étiquettes de l’INSEE, par ex. https://www.insee.fr/fr/information/2560625#titre-bloc-7
# NB. Écrit pour fonctionner aussi avec `france{AAAA}.txt en entrée.
def insert_insee_commune(db, COG_year, cursor):
    """ """
    print("BUILD INSEE REF: fill insee_commune\n===================================")
    with open('insee/{0}/comsimp{0}.txt'.format(COG_year)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        insee_code_list = []
        for row in reader:
            insee_COM = str(row['DEP']) + str(row['COM'])
            # Dans les listes des communes depuis 1943 (`france{AAAA}.txt`), des communes sont répétées pour
            # rendre compte des différentes fractions cantonales dans le temps.
            # ex. 278 codes commune sont répétés 3 à 13 fois dans `France2018.txt`
            # Simplification : on ne conserve conserve que la première occurrence de la liste.
            if insee_COM in insee_code_list:
                continue
            insee_code_list.append(insee_COM)
            # des communes dans un arrondissement (AR) mais hors canton (CT), et
            # des communes dans un CT mais hors AR
            AR_insee = row['AR'] if row['AR'] else None
            AR_id    = 'AR_'+row['DEP']+'-'+AR_insee if AR_insee else None
            CT_insee = row['CT'] if row['CT'] else None
            CT_id    = 'CT_' + row['DEP'] + '-' + CT_insee if CT_insee else None
            # cas des anciennes communes (anciens codes) localisées dans l’ancien département corse (20)
            REG_id   = 'REG_94' if row['DEP'] == '20' else 'REG_'+row['REG']
            try:
                cursor.execute("INSERT INTO insee_commune"
                               "(insee_code, REG_id, DEP_id, AR_id, CT_id, NCCENR, ARTMIN)"
                               "VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (insee_COM, REG_id, 'DEP_'+row['DEP'], AR_id, CT_id, row['NCCENR'], row['ARTMIN']))
            except sqlite3.IntegrityError as e:
                print(e, (": insee_code %s (%s) CT_id '%s' set to NULL" % (insee_COM, row['NCCENR'], CT_id)))
                cursor.execute("INSERT INTO insee_commune"
                               "(insee_code, REG_id, DEP_id, AR_id, CT_id, NCCENR, ARTMIN)"
                               "VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (insee_COM, REG_id, 'DEP_'+row['DEP'], AR_id, None, row['NCCENR'], row['ARTMIN']))
            db.commit()


"""
On récupère l’id de l’AR parent du CT dans la table insee_commune. Problème :
    * 17 Communes dépendent d’un CT mais pas d’un AR dans insee_commune (des cantons qui ne dépendent pas d’un arrondissement)
    * 255 CT restent sans AR parent après enrichissement (sans doute des CT listés in insee_ref, absent de insee_commune)
    * surtout, d’après le insee_commune (le référentiel INSEE), un même CT peut-être rattaché à des AR différents… (ex CT_01-10)
TODO: comment régler cette absence de parent ?
    1. On créer un AR avec l’id unspecified_AR ?
    2. On considère que le CT est rattaché au DEP ? (sont parent_id devient celui d’un DEP et son level passe de 5 à 4)
    Problème, 2 peut-être faux (information simplement manquante dans insee_commune)
"""
def update_insee_ref(db, cursor):
    """ """
    # get CT parent_id in table insee_commune
    print("BUILD INSEE REF: set CT insee_ref.parent_id\n===========================================")
    cursor.execute("SELECT id FROM insee_ref WHERE type= 'CT'")
    for canton in cursor.fetchall():
        ct_id = canton[0]
        cursor.execute(("SELECT DISTINCT AR_id FROM insee_commune WHERE CT_id = '%s'" % ct_id))
        parents = cursor.fetchall() # possiblement plusieurs parents (AR) pour un même CT (étrange…)
        # trop compliqué: on ramasse le premier AR parent du CT si la liste de parents n’est pas vide, et si sa valeur n’est pas None
        parent_id = parents[0][0] if parents and parents[0][0] is not None else None
        # print(parent_id)
        # pour mémoire, plus simple avec MySQLdb:
        # parent_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        if parent_id is None:
            continue
        else:
            cursor.execute(("UPDATE insee_ref SET parent_id = '%s' WHERE id = '%s'" % (parent_id, ct_id)))
            db.commit()


def insert_longlat(db, cursor, method):
    """ """
    print("BUILD INSEE REF: set insee_commune.longlat\n==========================================")
    # on ne dispose pas des coords, on va les chercher sur https://api.gouv.fr/api/api-geo.html
    if method == 'api':
        cursor.execute("SELECT insee_code FROM insee_commune")
        for insee_code in cursor:
            insee_code = insee_code[0]
            longlat = get_longlat(insee_code)
            if longlat is not None:
                print("set %s longlat: %s" % (insee_code, longlat))
                cursor.execute(("UPDATE insee_commune SET longlat = '%s' WHERE insee_code = '%s'" % (longlat, insee_code)))
                db.commit()
            else:
                continue
    # on dispose du mapping insee_code/coordonnées in communes-longlat.tsv
    elif method == 'tsv':
        with open('../communes-longlat.tsv', 'r') as f:
            data = csv.reader(f, delimiter="\t")
            for row in data:
                insee_code = row[0]
                longlat = row[1]
                print("set %s longlat: %s" % (insee_code, longlat))
                cursor.execute(("UPDATE insee_commune SET longlat = '%s' WHERE insee_code = '%s'" % (longlat, insee_code)))
                db.commit()
    else:
        return


def get_longlat(insee_code):
    """ """
    getGeo = 'https://geo.api.gouv.fr/communes/%s?fields=centre&format=json&geometry=centre' % insee_code
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
