# -*- coding: utf-8 -*-
import sqlite3
from lxml import etree
from lxml.etree import tostring
import io
import re
import csv


def insert_bibl(db, cursor, dt_id):
    """ """
    with open('bibl_gallica.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            if row['abbr'] == dt_id:
                cursor.execute(
                    "INSERT INTO bibl (abbr, bibl, bnf_catalogue_ark, gallica_ark, gallica_page_one, gallica_IIIF_availability)"
                    "VALUES(?, ?, ?, ?, ?, ?)",
                    (row['abbr'],
                     row['bibl'],
                     row['bnf_catalogue_ark'],
                     row['gallica_ark'],
                     row['gallica_page_one'],
                     row['gallica_IIIF_availability'])
                )
                db.commit()


def insert_place_values(db, cursor, dt_id):
    """ """
    print("INSERT bibl for {0}".format(dt_id))
    insert_bibl(db, cursor, dt_id)
    # store id of bibl
    bibl_id = cursor.lastrowid

    print("** TABLE place, place_alt_label, place_feature_type – INSERT")
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/'+dt_id+'.xml')
    # on enregistre le code du dpt
    dpt = tree.xpath('/DICTIONNAIRE')[0].get('dep')

    for entry in tree.xpath('/DICTIONNAIRE/article'):
        # un dictionnaire pour stocker les données relative à chaque nom de lieu
        place = {}

        # id de l’article in XML (e.g. 'DT02-00001')
        place['id'] = entry.get('id')

        # code insee de la commune identifiée dans le champ localisation
        # (ie. code insee de la commune d’appartenance du lieu dit…)
        place['localization_commune_insee_code'] = entry.xpath('definition/localisation/commune')[0].get('insee') \
            if entry.xpath('definition/localisation/commune') \
            else None
        # sortir les codes erreur
        # TODO: revoir avec CB et JP ces valeurs, en particulier 'commune_is_empty' – documenter.
        control_vals = ['too_many_insee_codes', 'article_not_found', 'commune_is_empty']
        if place['localization_commune_insee_code'] in control_vals:
            place['localization_commune_insee_code'] = None

        # degré de certitude de la localisation (commune attribuée au lieu)
        localization_certainty = entry.xpath('definition/localisation/commune')[0].get('precision') \
            if entry.xpath('definition/localisation/commune') \
            else None
        if localization_certainty == 'approximatif':
            place['localization_certainty'] = 'low'
        elif localization_certainty == 'certain':
            place['localization_certainty'] = 'high'
        else:
            place['localization_certainty'] = None

        # definition (tei:def)
        insee_pattern = re.compile('[0-9]{5}')
        remove_tags = re.compile('</?(definition|localisation|date|commune)[^>]*>')
        rename_commune_optag = re.compile('<commune [^ ]+ insee="([^"]+)"[^>]*>')
        rename_commune_cltag = re.compile('</commune>')
        rename_typo_tag = re.compile('<(/?)typologie[^>]*>')
        if entry.xpath('definition'):
            place['desc'] = tostring(entry.xpath('definition')[0], encoding='unicode')
            place['desc'] = ' '.join(place['desc'].split())
            # ATTENTION à la l’ordre des replace !!! (on réécrit commune avant de la supprimer…)
            if place['localization_commune_insee_code'] and insee_pattern.match(place['localization_commune_insee_code']):
                place['desc'] = re.sub(rename_commune_optag, '<a href="\\1">', place['desc'])
                place['desc'] = re.sub(rename_commune_cltag, '</a>', place['desc'])
            place['desc'] = re.sub(rename_typo_tag, '<\\1a>', place['desc'])
            place['desc'] = re.sub(remove_tags, '', place['desc'])
        else:
            place['desc'] = None

        # id du département
        place['dpt'] = dpt

        # page de début
        place['num_start_page'] = entry.get('pg')

        # la vedette principale (la première)
        # TODO: voir avec OC les différentes possibilités de ponctuation à la fin de la vedette ([,.…;:]) -> on supprime tout ?
        # TODO: voir les cas compliqués avec OC, par ex. DT10-02266 (pas de normalisation de la forme alternative)
        place['label'] = entry.xpath('vedette/sm[1]')[0].text.rstrip(',')
        place['label'] = place['label'].strip()
        # DT01 : des labels préfixés avec "*" (les formes reconstituées/hypothétiques pour les lieux disparus, selon SN)
        # place['label'] = format(place['label'][1:] if place['label'].startswith('*') else place['label'])
        # Parfois à la fin de la vedette (cf DT72), plus radical :
        place['label'] = place['label'].replace('*', '')

        # code insee (si commune, optionnel)
        place['commune_insee_code'] = entry.xpath('insee')[0].text if entry.xpath('insee') else None

        # les vedettes secondaires (optionnel, mais fréquent)
        place['alt_labels'] = []
        for i in entry.xpath('vedette//sm[position()>1]'):
            place['alt_labels'].append(i.text.rstrip(','))

        # feature types
        place['feature_types'] = []
        for i in entry.xpath('definition/typologie'):
            place['feature_types'].append(i.text.rstrip(','))

        # COMMENTAIRE**S**
        # possiblement plusieurs commentaires et plusieurs paragraphes par commentaire (//commentaire[2]/p[2])
        # un html5:article par commentaire, avec html5:p
        # NB. impossible de déterminer sur quoi porte un commentaire (l’article, la forme ?)

        # conversion HTML5 de chaque commentaire
        # contient els: p, pg, date, forme_ancienne2, i, sm, sup, note, reference, renvoi
        # TODO: REPRENDRE LA TRANSFORMATION DES RENVOIS POUR LANCER LA RECHERCHE SUR LE BON DPT
        # TODO: certains renvois dans //renvoi/i (et non //renvoi/sm) : normaliser XML ?
        commentaire2html = io.StringIO('''\
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:output method="text"/>
                <xsl:template match="/">
                    <xsl:text>&lt;article></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/article></xsl:text>
                </xsl:template>
                <xsl:template match="pg"/>
                <xsl:template match="p">
                    <xsl:text>&lt;p></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/p></xsl:text>
                </xsl:template>
                <xsl:template match="forme_ancienne2">
                    <xsl:text>&lt;dfn></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/dfn></xsl:text>
                </xsl:template>
                <xsl:template match="reference">
                    <xsl:text>&lt;cite></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/cite></xsl:text>
                </xsl:template>
                <xsl:template match="renvoi">
                    <xsl:apply-templates/>
                </xsl:template>
                <xsl:template match="sm[parent::renvoi]">
                    <xsl:text>&lt;a href="</xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>"></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/a></xsl:text>
                </xsl:template>
                    <xsl:template match="note">
                    <xsl:text>&lt;span class="note"></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/span></xsl:text>
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
                <xsl:template match="date">
                    <xsl:text>&lt;time></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/time></xsl:text>
                </xsl:template>
            </xsl:stylesheet>''')
        xslt_commentaire2html = etree.parse(commentaire2html)
        transform_commentaire2html = etree.XSLT(xslt_commentaire2html)

        place['comment'] = ''
        if entry.xpath('commentaire'):
            for commentaire in entry.xpath('commentaire'):
                comment = str(transform_commentaire2html(commentaire)).strip()
                # remove multiple spaces
                comment = " ".join(comment.split())
                # hack bad XML format (plus à ça près)
                comment = comment.replace('.</a>', '</a>.')
                comment = comment.replace('.">', '">')
                comment = comment.replace(' <sup>', '<sup>')
                # optimiser append
                place['comment'] += comment
        else:
            place['comment'] = None

        # INSERTIONS
        try:
            cursor.execute(
                "INSERT INTO place ("
                    "place_id,"
                    "label,"
                    "country,"
                    "dpt,"
                    "commune_insee_code,"
                    "localization_commune_insee_code,"
                    "localization_certainty,"
                    "desc,"
                    "num_start_page,"
                    "comment,"
                    "bibl_id)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (place['id'],
                     place['label'],
                     'FR',
                     place['dpt'],
                     place['commune_insee_code'],
                     place['localization_commune_insee_code'],
                     place['localization_certainty'],
                     place['desc'],
                     place['num_start_page'],
                     place['comment'],
                     bibl_id))
        except sqlite3.IntegrityError as e:
            print(e, "place %s" % (place['id']))
        db.commit()

        # insert secondary labels
        if place['alt_labels']:
            for alt_label in place['alt_labels']:
                cursor.execute("INSERT INTO place_alt_label (place_id, label) VALUES (?, ?)", (place['id'], alt_label))
                db.commit()

        # insert feature types
        if place['feature_types']:
            for feature_type in place['feature_types']:
                try:
                    cursor.execute("INSERT INTO place_feature_type (place_id, term) VALUES (?, ?);", (place['id'], feature_type))
                except sqlite3.IntegrityError as e:
                    print(e, (": place %s – FT '%s'" % (place['id'], feature_type)))
                db.commit()


# Ramasser le entry.localization_place_id (référence interne de la commune de rattachement)
def update_localization_place_id(db, cursor, dpt_code):
    """ """
    print("** TABLE place – SET localization_place_id, dpt "+dpt_code)
    # MySQL
    add_localization_place_id = """UPDATE place AS a
        INNER JOIN place AS b
        ON a.localization_commune_insee_code = b.commune_insee_code
        SET a.localization_place_id = b.place_id"""
    # SQLite3
    add_localization_place_id = """UPDATE place
        SET localization_place_id = (SELECT place_id
            FROM place as t2
            WHERE (place.localization_commune_insee_code = t2.commune_insee_code))
        WHERE
            place.dpt = '%s'
            AND
            EXISTS (SELECT * FROM place as t2
                WHERE (place.localization_commune_insee_code = t2.commune_insee_code))""" % dpt_code
    # on abandonne la résolution 100% sqlite
    #cursor.execute(add_localization_place_id)
    #db.commit()

    # approche 2 / perfs incomparables – todo: valider le résultat
    # dico: {'insee_code': 'place_id',…}, ie {'02001': 'DT02-00009', '02002': 'DT02-00017', '02003': 'DT02-00023'}
    map_DT_insee = {}
    for row in cursor.execute("""SELECT commune_insee_code, place_id
                              FROM place
                              WHERE commune_insee_code IS NOT NULL
                              AND dpt = '%s'""" % dpt_code):
        map_DT_insee[row[0]] = row[1]

    for insee_code, place_id in map_DT_insee.items():
        add_localization_place_id = """UPDATE place
            SET localization_place_id = '%s'
            WHERE localization_commune_insee_code = '%s'""" % (place_id, insee_code)
        #print(add_localization_place_id)
        cursor.execute(add_localization_place_id)
    db.commit()


def insert_place_old_label(db, cursor, dt_id):
    """ """
    print("** TABLE place_old_label – INSERT")
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
    clean_start = re.compile('^[—\- ]+')
    clean_end = re.compile('[— .,;]+$')
    clean_markup = re.compile(',(</[^>]+>)') # sortir la virgule du markup (span, cite, dfn, ?)

    # utilitaires pour extraire et nettoyer les formes anciennes
    # relou, support xpath incomplet, on ne peut pas sortir le texte qui suit le dernier élément <i>
    # <xsl:template match="i[position()=last()]/following-sibling::text()"/>
    # On corrige plus loin en traitement de chaîne de chars.
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
        place = {}
        # id de l’article
        place['id'] = entry.get('id')

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
                old_label_id = place['id']+'-0'+str(n) if n < 10 else place['id']+'-'+str(n)
                old_label_xml_str = tostring(old_label, encoding='unicode')
                old_label_xml_str = ' '.join(old_label_xml_str.split())
                tree = etree.fromstring(old_label_xml_str)
                # tout le contenu de l’élément forme_ancienne, formaté en HTML
                old_label_html_str = str(transform_old_label2html(tree))
                old_label_html_str = re.sub(clean_start, '', old_label_html_str)
                old_label_html_str = re.sub(clean_markup, '\\1,', old_label_html_str) # sortir les virgules des balises
                old_label_html_str = re.sub(clean_end, '', old_label_html_str)
                old_label_html_str = "<p>%s</p>" % (old_label_html_str) # on encapsule dans un <p> ? dans <li> ? Todo: à (re)voir
                # sortir les préfixes "*" des formes anciennes et les conserver dans les références (moche)
                old_label_html_str = old_label_html_str.replace('<dfn>*', '<dfn>')

                # tout le contenu de l’élément forme_ancienne, dépouillé des balises
                old_label_nude_str = re.sub(tags, '', old_label_html_str)
                # DFN
                # TODO: extraire tous les dfn du champ dans une table dédiée pour indexation
                dfn = str(transform_old_label2dfn(tree))
                dfn = re.sub(clean_start, '', dfn)
                dfn = dfn.replace('<dfn>*', '<dfn>') # déprime de la gestion de l’"*" initiale (cf plus haut aussi)
                dfn = dfn.replace(',</dfn>', '</dfn>,') # sortir la ponctuation avant normalisation de la fin de la chaîne
                dfn = re.sub(clean_end, '', dfn)
                dfn = dfn.rstrip()  # ceintures bretelles
                # On vire le texte qui suit le dernier élément <dfn> (support xpath insuffisant avec lxml)
                pos = dfn.rfind('</dfn>')
                dfn = dfn[:pos+6]
                # 7201 formes anciennes font plus de 100 chars : on coupe !
                # TODO: corriger XML ou le code de chargement pour repositionner les balises dans la chaîne conservée
                # use iterator: re.finditer('</dfn>', dfn)
                if len(dfn) > 100:
                    # on vire les balises, pour rien risquer…
                    dfn = re.sub(tags, '', dfn)
                    dfn = dfn[:100].strip() + '…'
                # quand label du toponyme ancien est vide, on reprend celui de la vedette
                # TODO: essayer d’affiner cette logique avec OC et SN
                if not dfn:
                    dfn = entry.xpath('vedette/sm[1]')[0].text.rstrip(',')
                    dfn = dfn.strip()
                    # print(placename['id']+' forme_ancienne sans label => '+dfn)

                # DATE – Attention au mauvais formatage des dates dans les XML (des sauts de lignes intempestifs…)
                # TODO: du code pour normaliser les dates "textuelles"
                rich_date = str(transform_old_label2rich_date(tree)).lstrip()
                date = re.sub(tags, '', rich_date)
                # remove multiple spaces
                date = " ".join(date.split())
                # print(rich_date + ' = ' + date)
                # Ref (référence de la forme ancienne) ; 1 forme_ancienne avec plus d’une réf ! (pour l’instant, on les vire = choix du prestataire d’ailleurs…)
                # contenu riche : i, sup, pg (on les sort en XSLT), date, sm
                rich_ref = str(transform_old_label2rich_ref(tree)).strip()
                rich_ref = rich_ref.lstrip('(').rstrip(')') # suppression des parenthèses
                rich_ref = rich_ref.replace(',</cite>', '</cite>,')  # sortir la ponctuation du titre
                # ref = re.sub(tags, '', rich_ref)
                n += 1
                i += 1
                try:
                    cursor.execute(
                        "INSERT INTO place_old_label ("
                            "old_label_id,"
                            "place_id,"
                            "rich_label,"
                            "rich_date,"
                            "text_date,"
                            "rich_reference,"
                            "rich_label_node,"
                            "text_label_node)"
                        "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (old_label_id,
                             place['id'],
                             dfn,
                             rich_date,
                             date,
                             rich_ref,
                             old_label_html_str,
                             old_label_nude_str))
                except sqlite3.IntegrityError as e:
                    print(e, "place %s" % (place['id']))
                db.commit()

        else:
            continue

    # Remettre les valeurs vides à NULL… honteux et efficace:
    cursor.execute("""
        UPDATE place_old_label
        SET
        rich_date = CASE rich_date WHEN '' THEN NULL ELSE rich_date END,
        text_date = CASE text_date WHEN '' THEN NULL ELSE text_date END,
        rich_reference = CASE rich_reference WHEN '' THEN NULL ELSE rich_reference END
    """)
    db.commit()
    # db.close()

