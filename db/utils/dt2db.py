import MySQLdb
from lxml import etree
from lxml.etree import tostring
import re
import os
import insee

"""
pour le nommage des champs, on privilégie la sémantique TEI en prévision du mapping en sortie
    * entry: une entrée du dictionnaire (un article) (body/entry)
    * entry-id: l’identifiant de l’articcle (entry/@xml:id)
    * orth: vedette (entry/form/orth)
"""

# TODO: prendre en charge les commentaires (parfois in p mais pas tjs ; analyser la structuration (quelles balises)

# Ouverture de la connection
db = MySQLdb.connect("localhost","root","rootroot","dicotopo" )
db.set_character_set('utf8')
cursor = db.cursor()
cursor.execute('SET NAMES UTF8MB4;')
cursor.execute('SET CHARACTER SET UTF8MB4;')
cursor.execute('SET character_set_connection=UTF8MB4;')

# Import des données INSEE: obligatoire pour les contraintes (respecter cet ordre)
print('création des tables de référence insee')
insee.create_insee_ref(db, cursor)
insee.insert_insee_ref(db, cursor)
insee.create_insee_communes(db, cursor)
insee.insert_insee_communes(db, cursor)
insee.update_insee_ref(db, cursor)

# enrichissement: ajout des coordonnées (method='api|tsv')
print('ajout des coordonnées à la table de référence insee des communes')
insee.insert_longlat(db, cursor, 'tsv')


# création des tables pour les DT
print('création des tables dicotopo')
sqlFile = open('datamodel.sql', 'r')
sql = sqlFile.read()
sqlFile.close()
sqlCmds = sql.split(';')
# quick and dirty [:-1] pour ne pas envoyer une requête vide correspondant à l’item vide après le dernier ";" du datamodel.sql
for cmd in sqlCmds[:-1]:
    cursor.execute(cmd)
    db.commit()


tree = etree.parse("../dico-topo/data/DT02/DT02.xml")
# on enregistre le code du dpt
dpt = tree.xpath("/DICTIONNAIRE")[0].get("dep")

for entry in tree.xpath("/DICTIONNAIRE/article"):
    # un dictionnaire pour stocker les données relative à chaque article
    art = {}
    # id de l’article
    art["id"] = entry.get("id")

    # localisation ("commune de…") ; code de la localisation et degré de certitude
    art["localization"] = []
    for i in entry.xpath("definition/localisation"):
        art["localization"].append(i.text)
    # print(art["localization"])

    # code insee de la commune identifiée dans le champ localisation
    # (ie. code insee de la commune d’appartenance du lieu dit…)
    art["localization_insee"] = entry.xpath("definition/localisation/commune")[0].get("insee") if entry.xpath("definition/localisation/commune") else None

    # degré de certitude de la localisation (commune attribuée au lieu) ; verbeux pour redéfinir la sémantique contenue dans les XML
    localization_certainty = entry.xpath("definition/localisation/commune")[0].get("precision")\
        if entry.xpath("definition/localisation/commune")\
        else None
    if localization_certainty == "approximatif": art["localization_certainty"] = 'low'
    elif localization_certainty == "certain": art["localization_certainty"] = 'high'
    else: art["localization_certainty"] = None

    # definition (tei:def)
    insee_pattern = re.compile('[0-9]{5}')
    remove_tags = re.compile('</?(definition|localisation|date|commune)[^>]*>')
    rename_commune_optag  = re.compile('<commune [^ ]+ insee="([^"]+)"[^>]*>')
    rename_commune_cltag = re.compile('</commune>')
    rename_typo_tag = re.compile('<(/?)typologie[^>]*>')
    if entry.xpath("definition"):
        art["def"] = tostring(entry.xpath("definition")[0], encoding='unicode')
        art["def"] = " ".join(art["def"].split())
        # ATTENTION à la l’ordre des replace !!! (on réécrit commune avant de la supprimer…)
        if art["localization_insee"] and insee_pattern.match(art["localization_insee"]):
            art["def"] = re.sub(rename_commune_optag, '<a href="\\1">', art["def"])
            art["def"] = re.sub(rename_commune_cltag, '</a>', art["def"])
        art["def"] = re.sub(rename_typo_tag, '<\\1a>', art["def"])
        art["def"] =  re.sub(remove_tags, '', art["def"])
    else: art["def"] =  None
    # print(art["def"])

    # id du département
    art["dpt"] = dpt

    # page de début
    art["start-page"] = entry.get("pg")

    # la vedette principale (la première)
    art["orth"] = entry.xpath("vedette/sm[1]")[0].text.rstrip(',')

    # code insee (si commune, optionnel)
    art["insee"] = entry.xpath("insee")[0].text if entry.xpath("insee") else None

    # les vedettes secondaires (alt_orth) (optionnel, mais fréquent)
    art["alt_orth"] = []
    for i in entry.xpath("vedette//sm[position()>1]"):
        art["alt_orth"].append(i.text.rstrip(','))

    # feature types
    art["keywords"] = []
    for i in entry.xpath("definition/typologie"):
        art["keywords"].append(i.text.rstrip(','))

    # print(art)


    """
    ======================
    INSERTION
    ======================
    """

    # insert entry
    try:
        cursor.execute(
            "INSERT INTO entry (entry_id, orth, country, dpt, insee, localization_insee, localization_certainty, def)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (art["id"], art["orth"], 'FR', art["dpt"], art["insee"], art["localization_insee"], art["localization_certainty"], art["def"]))
    # CATCH très sale pour les REFENCES INCONNUES
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(("IntegrityError (Foreign Key). %s, unknow localization_insee REFERENCES insee_communes.insee_id: %s" % (art["id"], art["localization_insee"])))
        cursor.execute(
            "INSERT INTO entry (entry_id, orth, country, dpt, insee, localization_insee, localization_certainty)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (art["id"], art["orth"], 'FR', art["dpt"], art["insee"], None, None))
        continue
    db.commit()

    # référence interne de la commune de rattachement (index nécessaire)
    add_localization_entry_id = """UPDATE entry AS a
      INNER JOIN entry AS b ON a.localization_insee = b.insee
      SET a.localization_entry_id = b.entry_id"""
    cursor.execute(add_localization_entry_id)
    db.commit()

    # insert secondary_orth
    if art["alt_orth"]:
        for alt_orth in art["alt_orth"]:
            cursor.execute("INSERT INTO alt_orth (entry_id, alt_orth) VALUES (%s, %s)", (art["id"], alt_orth))
            db.commit()

    # insert keywords (feature types)
    if art["keywords"]:
        for term in art["keywords"]:
            cursor.execute("INSERT INTO keywords (entry_id, term) VALUES (%s, %s);", (art["id"], term))
            db.commit()

db.close()
# moche!
os.system("python ref.py")


