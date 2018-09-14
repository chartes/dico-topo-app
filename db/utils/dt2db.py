# -*- coding: utf-8 -*-
import sqlite3
from lxml import etree
from lxml.etree import tostring
import re
import io


def insert_placename_values(db, cursor, dt_id):
    """ """
    print("FILL TABLES placename, placename_alt_label, feature_type"
          "\n========================================================")
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/'+dt_id+'.xml')
    # on enregistre le code du dpt
    dpt = tree.xpath('/DICTIONNAIRE')[0].get('dep')

    for entry in tree.xpath('/DICTIONNAIRE/article'):
        # un dictionnaire pour stocker les données relative à chaque nom de lieu
        placename = {}

        # id de l’article in XML (e.g. 'DT02-00001')
        placename['id'] = entry.get('id')

        # code insee de la commune identifiée dans le champ localisation
        # (ie. code insee de la commune d’appartenance du lieu dit…)
        placename['localization_commune_insee_code'] = entry.xpath('definition/localisation/commune')[0].get('insee') \
            if entry.xpath('definition/localisation/commune') \
            else None
        # sortir les codes erreur
        control_vals = ['too_many_insee_codes', 'article_not_found']
        if placename['localization_commune_insee_code'] in control_vals:
            placename['localization_commune_insee_code'] = None

        # degré de certitude de la localisation (commune attribuée au lieu)
        localization_certainty = entry.xpath('definition/localisation/commune')[0].get('precision') \
            if entry.xpath('definition/localisation/commune') \
            else None
        if localization_certainty == 'approximatif':
            placename['localization_certainty'] = 'low'
        elif localization_certainty == 'certain':
            placename['localization_certainty'] = 'high'
        else:
            placename['localization_certainty'] = None

        # definition (tei:def)
        insee_pattern = re.compile('[0-9]{5}')
        remove_tags = re.compile('</?(definition|localisation|date|commune)[^>]*>')
        rename_commune_optag = re.compile('<commune [^ ]+ insee="([^"]+)"[^>]*>')
        rename_commune_cltag = re.compile('</commune>')
        rename_typo_tag = re.compile('<(/?)typologie[^>]*>')
        if entry.xpath('definition'):
            placename['desc'] = tostring(entry.xpath('definition')[0], encoding='unicode')
            placename['desc'] = ' '.join(placename['desc'].split())
            # ATTENTION à la l’ordre des replace !!! (on réécrit commune avant de la supprimer…)
            if placename['localization_commune_insee_code'] and insee_pattern.match(placename['localization_commune_insee_code']):
                placename['desc'] = re.sub(rename_commune_optag, '<a href="\\1">', placename['desc'])
                placename['desc'] = re.sub(rename_commune_cltag, '</a>', placename['desc'])
            placename['desc'] = re.sub(rename_typo_tag, '<\\1a>', placename['desc'])
            placename['desc'] = re.sub(remove_tags, '', placename['desc'])
        else:
            placename['desc'] = None

        # id du département
        placename['dpt'] = dpt

        # page de début
        placename['num_start_page'] = entry.get('pg')

        # la vedette principale (la première)
        placename['label'] = entry.xpath('vedette/sm[1]')[0].text.rstrip(',')

        # code insee (si commune, optionnel)
        placename['commune_insee_code'] = entry.xpath('insee')[0].text if entry.xpath('insee') else None

        # les vedettes secondaires (optionnel, mais fréquent)
        placename['alt_labels'] = []
        for i in entry.xpath('vedette//sm[position()>1]'):
            placename['alt_labels'].append(i.text.rstrip(','))

        # feature types
        placename['feature_types'] = []
        for i in entry.xpath('definition/typologie'):
            placename['feature_types'].append(i.text.rstrip(','))

        # comment(s?)
        # TODO: format, contient els: date, forme_ancienne2, i, note, p, pg, reference, renvoi, sm, sup
        # ATTENTION: //article/commentaire[2] et //article/commentaire[3] ; contenu parfois important
        # pas évident de déterminer sur quoi porte le commentaire: l’article ? la forme ? – revoir
        placename['comment'] = tostring(entry.xpath('commentaire')[0], encoding='unicode') \
            if entry.xpath('commentaire') \
            else None

        # INSERTIONS
        try:
            cursor.execute(
                "INSERT INTO placename ("
                    "placename_id,"
                    "label,"
                    "country,"
                    "dpt,"
                    "commune_insee_code,"
                    "localization_commune_insee_code,"
                    "localization_certainty,"
                    "desc,"
                    "num_start_page,"
                    "comment)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (placename['id'],
                     placename['label'],
                     'FR',
                     placename['dpt'],
                     placename['commune_insee_code'],
                     placename['localization_commune_insee_code'],
                     placename['localization_certainty'],
                     placename['desc'],
                     placename['num_start_page'],
                     placename['comment']))
        except sqlite3.IntegrityError as e:
            print(e, "placename %s" % (placename['id']))
        db.commit()

        # insert secondary labels
        if placename['alt_labels']:
            for alt_label in placename['alt_labels']:
                cursor.execute("INSERT INTO placename_alt_label (placename_id, label) VALUES (?, ?)", (placename['id'], alt_label))
                db.commit()

        # insert feature types
        if placename['feature_types']:
            for feature_type in placename['feature_types']:
                cursor.execute("INSERT INTO feature_type (placename_id, term) VALUES (?, ?);", (placename['id'], feature_type))
                db.commit()


# Ramasser le entry.localization_placename_id (référence interne de la commune de rattachement)
def update_localization_placename_id(db, cursor):
    """ """
    print("TABLE placename: set localization_placename_id\n==============================================")
    # MySQL
    add_localization_placename_id = """UPDATE placename AS a
        INNER JOIN placename AS b
        ON a.localization_commune_insee_code = b.commune_insee_code
        SET a.localization_placename_id = b.placename_id"""
    # SQLite3
    add_localization_placename_id = """UPDATE placename
        SET localization_placename_id = (SELECT placename_id
            FROM placename as t2
            WHERE (placename.localization_commune_insee_code = t2.commune_insee_code))
        WHERE EXISTS (SELECT *
            FROM placename as t2
            WHERE (placename.localization_commune_insee_code = t2.commune_insee_code))"""
    cursor.execute(add_localization_placename_id)
    db.commit()


def insert_placename_old_label(db, cursor, dt_id):
    """ """
    print("TABLE placename_old_label: set values\n=====================================")
    tags = re.compile('<[^>]+>')
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/'+dt_id+'.xml')
    # on enregistre le code du dpt
    # dpt = tree.xpath('/DICTIONNAIRE')[0].get('dep')

    # conversion HTML5 de toute l’entrée forme_ancienne
    old_label2html = io.StringIO('''\
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="text"/>
            <xsl:template match="/">
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="sup">
                <xsl:text>&lt;sup></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/sup></xsl:text>
            </xsl:template>
            <xsl:template match="sm">
                <xsl:text>&lt;span class="sc"></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/span></xsl:text>
            </xsl:template>
            <xsl:template match="i">
                <xsl:text>&lt;i></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/i></xsl:text>
            </xsl:template>
            <xsl:template match="i[parent::forme_ancienne]">
                <xsl:text>&lt;dfn></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/dfn></xsl:text>
            </xsl:template>
            <xsl:template match="i[parent::reference]">
                <xsl:text>&lt;cite></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/cite></xsl:text>
            </xsl:template>
            <xsl:template match="date">
                <xsl:text>&lt;time></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/time></xsl:text>
            </xsl:template>
            <xsl:template match="comment">
                <xsl:text>&lt;br/></xsl:text>
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="pg"/>
        </xsl:stylesheet>''')
    xslt_old_label2html = etree.parse(old_label2html)
    transform_old_label2html = etree.XSLT(xslt_old_label2html)
    # nettoyage typo, réutilisable
    clean_start = re.compile('^[— ]+')
    clean_end = re.compile('[— .,;]+$')
    clean_markup = re.compile(',(</[^>]+>)') # sortir la virgule du markup (span, cite, dfn, ?)

    # utilitaires pour extraire et nettoyer les formes anciennes
    get_old_label = io.StringIO('''\
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="text"/>
            <xsl:template match="/">
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="i">
                <xsl:text>&lt;dfn></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/dfn></xsl:text>
            </xsl:template>
            <xsl:template match="reference"/>
            <xsl:template match="date"/>
            <xsl:template match="comment"/>
            <xsl:template match="pg"/>
        </xsl:stylesheet>''')
    xslt_get_old_label = etree.parse(get_old_label)
    transform_old_label2dfn = etree.XSLT(xslt_get_old_label)

    get_old_label_rich_date = io.StringIO('''\
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="text"/>
            <xsl:template match="/forme_ancienne">
                <xsl:apply-templates select="date[1]"/>
            </xsl:template>
            <xsl:template match="date">
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="sup">
                <xsl:text>&lt;sup></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/sup></xsl:text>
            </xsl:template>
            <xsl:template match="sm">
                <xsl:text>&lt;span class="sc"></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/span></xsl:text>
            </xsl:template>
        </xsl:stylesheet>''')
    xslt_get_old_label_rich_date = etree.parse(get_old_label_rich_date)
    transform_old_label2rich_date = etree.XSLT(xslt_get_old_label_rich_date)

    get_old_label_rich_ref = io.StringIO('''\
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="text"/>
            <xsl:template match="/forme_ancienne">
                <xsl:apply-templates select="reference[1]"/>
            </xsl:template>
            <xsl:template match="reference">
                <xsl:apply-templates/>
            </xsl:template>
            <xsl:template match="pg"/>
            <xsl:template match="sup">
                <xsl:text>&lt;sup></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/sup></xsl:text>
            </xsl:template>
            <xsl:template match="i">
                <xsl:text>&lt;cite></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/cite></xsl:text>
            </xsl:template>
            <xsl:template match="sm">
                <xsl:text>&lt;span class="sc"></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/span></xsl:text>
            </xsl:template>
            <xsl:template match="date">
                <xsl:text>&lt;time></xsl:text>
                <xsl:apply-templates/>
                <xsl:text>&lt;/time></xsl:text>
            </xsl:template>
        </xsl:stylesheet>''')
    xslt_get_old_label_rich_ref = etree.parse(get_old_label_rich_ref)
    transform_old_label2rich_ref = etree.XSLT(xslt_get_old_label_rich_ref)

    i = 0
    for entry in tree.xpath('/DICTIONNAIRE/article'):
        # un dictionnaire pour stocker les données relative à chaque article
        placename = {}
        # id de l’article
        placename['id'] = entry.get('id')

        # formes anciennes et attestations
        # jusqu’à 47 formes anciennes pour une vedette, dans l’Aisne: `distinct-values(//article/count(forme_ancienne)`
        # des formes anciennes sans forme !!!, ex: DT02-04777
        # On garde 1 date et 1 ref par forme ancienne ; on place les rares exceptions dans le champs texte qu’on publiera

        # Source XML :
        #   <forme_ancienne>Inter <i>Estran</i> et <i>Abugniez</i> et <i>Gerigniez,</i>
        #       <date>1168</date>
        #       <reference>(cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36)</reference>.
        #   </forme_ancienne>
        #
        # Variables
        #   * old_label_id
        #       identifiant calculé de la forme ancienne
        #       DT02-00043-03
        #   * old_label_xml_str
        #       élément <forme_ancienne> dans la source XML
        #       <forme_ancienne>Inter <i>Estran</i> et <i>Abugniez</i> et <i>Gerigniez,</i> <date>1168</date> <reference>(cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36)</reference>.</forme_ancienne>
        #   * old_label_html_str
        #       élément <forme_ancienne> converti en HTML
        #       <p>Inter <dfn>Estran</dfn> et <dfn>Abugniez</dfn> et <dfn>Gerigniez</dfn>, <time>1168</time> (cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36)</p>
        #   * old_label_nude_str
        #       élément <forme_ancienne> sans balise
        #       Inter Estran et Abugniez et Gerigniez, 1168 (cart. de l’abb. de Thenailles, fos 15, 20, 36)
        #   * dfn
        #       la/les forme(s) d’une entrée forme ancienne, en HTML
        #       Inter <dfn>Estran</dfn> et <dfn>Abugniez</dfn> et <dfn>Gerigniez</dfn>
        #   * rich_ref
        #       la référence d’une entrée forme ancienne avec enrichissement typo, en HTML
        #       cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36
        #   * rich_date
        #       la date avec enrichissement typo, en HTML)
        #       <span class='sc">xiii</span><sup>e</sup> siècle (cf DT02-00048-03)
        #   * date
        #       la date sans enrichissement typo
        #       xiiie siècle (idem)
        if entry.xpath('forme_ancienne'):
            n = 1
            for old_label in entry.xpath('forme_ancienne'):
                old_label_id = placename['id']+'-0'+str(n) if n < 10 else placename['id']+'-'+str(n)
                old_label_xml_str = tostring(old_label, encoding='unicode')
                old_label_xml_str = ' '.join(old_label_xml_str.split())
                tree = etree.fromstring(old_label_xml_str)
                # tout le contenu de l’élément forme_ancienne, formaté en HTML
                old_label_html_str = str(transform_old_label2html(tree))
                old_label_html_str = re.sub(clean_start, '', old_label_html_str)
                old_label_html_str = re.sub(clean_markup, '\\1,', old_label_html_str) # sortir les virgules des balises
                old_label_html_str = re.sub(clean_end, '', old_label_html_str)
                old_label_html_str = "<p>%s</p>" % (old_label_html_str) # on encapsule dans un <p> ? dans <li> ? Todo: à (re)voir
                # tout le contenu de l’élément forme_ancienne, dépouillé des balises
                old_label_nude_str = re.sub(tags, '', old_label_html_str)
                # DFN
                # TODO: extraire tous les dfn du champ dans une table dédiée pour indexation
                dfn = str(transform_old_label2dfn(tree))
                dfn = re.sub(clean_start, '', dfn)
                dfn = dfn.replace(',</dfn>', '</dfn>,') # sortir la ponctuation avant normalisation de la fin de la chaîne
                dfn = re.sub(clean_end, '', dfn)
                # DATE – Attention au mauvais formatage des dates dans les XML (des sauts de lignes intempestifs…)
                # TODO: du code pour normaliser les dates "textuelles"
                rich_date = str(transform_old_label2rich_date(tree))
                date = re.sub(tags, '', rich_date)
                # print(rich_date + ' = ' + date)
                # Ref (référence de la forme ancienne) ; 1 forme_ancienne avec plus d’une réf ! (pour l’instant, on les vire = choix du prestataire d’ailleurs…)
                # contenu riche : i, sup, pg (on les sort en XSLT), date, sm
                rich_ref = str(transform_old_label2rich_ref(tree)).strip()
                rich_ref = rich_ref.lstrip('(').rstrip(')') # suppression des parenthèses
                rich_ref = rich_ref.replace(',</cite>', '</cite>,')  # sortir la ponctuation du titre
                # ref = re.sub(tags, '', rich_ref)
                n += 1
                i += 1
                cursor.execute(
                    "INSERT INTO placename_old_label ("
                        "old_label_id,"
                        "placename_id,"
                        "rich_label,"
                        "rich_date,"
                        "text_date,"
                        "rich_reference,"
                        "rich_label_node,"
                        "text_label_node)"
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                        (old_label_id,
                         placename['id'],
                         dfn,
                         rich_date,
                         date,
                         rich_ref,
                         old_label_html_str,
                         old_label_nude_str))
                db.commit()

        else:
            continue

    # Remettre les valeurs vides à NULL… Un peu la honte, mais efficace:
    cursor.execute("""
        UPDATE placename_old_label
        SET
        rich_date = CASE rich_date WHEN '' THEN NULL ELSE rich_date END,
        text_date = CASE text_date WHEN '' THEN NULL ELSE text_date END,
        rich_reference = CASE rich_reference WHEN '' THEN NULL ELSE rich_reference END
    """)
    db.commit()
    db.close()
