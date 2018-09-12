import sqlite3
from lxml import etree
from lxml.etree import tostring
import re

# parser le XML et stocker les valeurs à insérer en base
def insert_entry_values(db, cursor, dt_id):
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/'+dt_id+'.xml')
    # on enregistre le code du dpt
    dpt = tree.xpath("/DICTIONNAIRE")[0].get("dep")

    for entry in tree.xpath("/DICTIONNAIRE/article"):
        # un dictionnaire pour stocker les données relative à chaque article
        art = {}

        # id de l’article in XML (e.g. 'DT02-00001')
        art["id"] = entry.get("id")

        # INUTILE???? localisation ("commune de…") ; code de la localisation et degré de certitude
        art["localization"] = []
        for i in entry.xpath("definition/localisation"):
            art["localization"].append(i.text)

        # code insee de la commune identifiée dans le champ localisation
        # (ie. code insee de la commune d’appartenance du lieu dit…)
        art["localization_insee_id"] = entry.xpath("definition/localisation/commune")[0].get("insee") if entry.xpath(
            "definition/localisation/commune") else None
        #print(art["localization_insee_id"])
        #continue

        # degré de certitude de la localisation (commune attribuée au lieu) ; verbeux pour redéfinir la sémantique contenue dans les XML
        localization_certainty = entry.xpath("definition/localisation/commune")[0].get("precision") \
            if entry.xpath("definition/localisation/commune") \
            else None
        if localization_certainty == "approximatif":
            art["localization_certainty"] = 'low'
        elif localization_certainty == "certain":
            art["localization_certainty"] = 'high'
        else:
            art["localization_certainty"] = None

        # definition (tei:def)
        insee_pattern = re.compile('[0-9]{5}')
        remove_tags = re.compile('</?(definition|localisation|date|commune)[^>]*>')
        rename_commune_optag = re.compile('<commune [^ ]+ insee="([^"]+)"[^>]*>')
        rename_commune_cltag = re.compile('</commune>')
        rename_typo_tag = re.compile('<(/?)typologie[^>]*>')
        if entry.xpath("definition"):
            art["def"] = tostring(entry.xpath("definition")[0], encoding='unicode')
            art["def"] = " ".join(art["def"].split())
            # ATTENTION à la l’ordre des replace !!! (on réécrit commune avant de la supprimer…)
            if art["localization_insee_id"] and insee_pattern.match(art["localization_insee_id"]):
                art["def"] = re.sub(rename_commune_optag, '<a href="\\1">', art["def"])
                art["def"] = re.sub(rename_commune_cltag, '</a>', art["def"])
            art["def"] = re.sub(rename_typo_tag, '<\\1a>', art["def"])
            art["def"] = re.sub(remove_tags, '', art["def"])
        else:
            art["def"] = None

        # id du département
        art["dpt"] = dpt

        # page de début
        art["start-pg"] = entry.get("pg")

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

        # INSERTIONS
        try:
            cursor.execute(
                "INSERT INTO entry (entry_id, orth, country, dpt, insee_id, localization_insee_id, localization_certainty, def, start_pg)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (art["id"], art["orth"], 'FR', art["dpt"], art["insee"], art["localization_insee_id"], art["localization_certainty"], art["def"], art["start-pg"]))
        # pb contrainte sur localization_insee_id: certains codes insee inscrits dans les XML (//definition/localisation/commune/@insee) sont absents du référentiels
        except sqlite3.IntegrityError as e:
            print(("IntegrityError (Foreign Key). %s, unknow localization_insee_id REFERENCES insee_commune.insee_id: %s" % (art["id"], art["localization_insee_id"])))
            cursor.execute(
                "INSERT INTO entry (entry_id, orth, country, dpt, insee_id, localization_insee_id, localization_certainty, def, start_pg)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (art["id"], art["orth"], 'FR', art["dpt"], art["insee"], None, None, art["def"], art["start-pg"]))
        db.commit()

        # insert secondary_orth
        if art["alt_orth"]:
            for alt_orth in art["alt_orth"]:
                cursor.execute("INSERT INTO alt_orth (entry_id, alt_orth) VALUES (?, ?)", (art["id"], alt_orth))
                db.commit()

        # insert keywords (feature types)
        if art["keywords"]:
            for term in art["keywords"]:
                cursor.execute("INSERT INTO keywords (entry_id, term) VALUES (?, ?);", (art["id"], term))
                db.commit()


# Ramasser le entry.localization_entry_id (référence interne de la commune de rattachement) – index nécessaire
def fill_localisation_entry_id(db, cursor):
    # MySQL
    add_localization_entry_id = """UPDATE entry AS a
        INNER JOIN entry AS b
        ON a.localization_insee_id = b.insee_id
        SET a.localization_entry_id = b.entry_id"""
    # SQLite3
    add_localization_entry_id = """UPDATE entry
        SET localization_entry_id = (SELECT entry_id
            FROM entry as t2
            WHERE (entry.localization_insee_id = t2.insee_id))
        WHERE EXISTS (SELECT *
            FROM entry as t2
            WHERE (entry.localization_insee_id = t2.insee_id))"""
    cursor.execute(add_localization_entry_id)
    db.commit()