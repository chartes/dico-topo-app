# -*- coding: utf-8 -*-
import sqlite3
from lxml import etree
from lxml.etree import tostring
import io
import re
import csv
from datetime import datetime


def html_snippet_validator(html_snippet, place_id, authorized_tags_set):
    """ """
    html_snippet_p = '<p>' + html_snippet + '</p>'

    # Vérification de la conformité
    parser = etree.XMLParser()
    try:
        tree = etree.XML(html_snippet_p, parser)
    except:
        pass
    for error in parser.error_log:
        print('place', place_id, 'xml error:', error.message, '==>', html_snippet)

    # Vérification des balises
    tag = re.compile('<([^ >/]+)[^>]*>')
    html_snippet_tags_name = set(re.findall(tag, html_snippet_p))
    unauthorized_tags_set = html_snippet_tags_name.difference(authorized_tags_set)
    if len(unauthorized_tags_set):
        for unauthorized_tag in unauthorized_tags_set:
            print('place', place_id, 'html error:', unauthorized_tag, 'tag not authorized', '==>', html_snippet)


def date_4digits(date):
    """ """
    missing_zero_digit_number = 4 - len(date)
    date = missing_zero_digit_number*'0' + date
    return date


def date2iso(date):
    """ """
    year_pattern = re.compile('^[0-9]{3,4}$')
    approximate_date_pattern1 = re.compile('([0-9]{3,4}) environ')
    approximate_date_pattern2 = re.compile('vers ([0-9]{3,4})')
    interval_date_pattern = re.compile('([0-9]{3,4})-([0-9]{3,4})')
    century_date_pattern1 = re.compile('([ivxlcm]+)e siècle')
    century_date_pattern2 = re.compile('([0-9]{1,2})e')
    republican_calendar_pattern = re.compile('an ([ivx]+)')

    century_dict = {
        'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
        'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10',
        'xi': '11', 'xii': '12', 'xiii': '13', 'xiv': '14', 'xv': '15',
        'xvi': '16', 'xvii': '17', 'xviii': '18', 'xix': '19', 'xx': '20'}

    republican_calendar_dict = {
        'i': '1792/1793', 'ii': '1793/1794', 'iii': '1794/1795', 'iv': '1795/1796', 'v': '1796/1797',
        'vi': '1797/1798','vii': '1798/1799', 'viii': '1799/1800', 'ix': '1800/1801', 'x': '1801/1802',
        'xi': '1802/1803', 'xii': '1803/1804', 'xiii': '1804/1805', 'xiv': '1805/1806'}

    date = date.lower()
    if year_pattern.match(date):
        date_iso = date_4digits(re.search(year_pattern, date)[0])

    elif approximate_date_pattern1.match(date):
        # date_iso = re.sub(approximate_date_pattern1, '\\1~', date)
        date_iso = date_4digits(re.search(approximate_date_pattern1, date).group(1))+'~'

    elif approximate_date_pattern2.match(date):
        date_iso = date_4digits(re.search(approximate_date_pattern2, date).group(1)) + '~'

    elif interval_date_pattern.match(date):
        # date_iso = re.sub(interval_date_pattern, '\\1/\\2', date)
        start = date_4digits(re.search(interval_date_pattern, date).group(1))
        end = date_4digits(re.search(interval_date_pattern, date).group(2))
        date_iso = start + '/' + end

    elif century_date_pattern1.match(date):
        century = century_date_pattern1.search(date).group(1)
        date_iso = century_dict[century] if century in century_dict else None

    elif century_date_pattern2.match(date):
        date_iso = century_date_pattern2.search(date).group(1)

    elif republican_calendar_pattern.match(date):
        year = republican_calendar_pattern.search(date).group(1)
        date_iso = republican_calendar_dict[year] if year in republican_calendar_dict else None

    else:
        date_iso = None

    # return date, date_iso
    return date_iso


def insert_bibl(db, cursor, dt_id):
    """ """
    with open('bibl_gallica.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            if row['dt_id'] == dt_id:
                cursor.execute(
                    "INSERT INTO bibl (abbr,"
                        "bibl,"
                        "bnf_catalogue_ark,"
                        "gallica_ark,"
                        "gallica_page_one,"
                        "gallica_IIIF_availability)"
                    "VALUES(?, ?, ?, ?, ?, ?)",

                    (row['abbr'],
                     row['bibl'],
                     row['bnf_catalogue_ark'],
                     row['gallica_ark'],
                     row['gallica_page_one'],
                     row['gallica_IIIF_availability'])
                )
                db.commit()


def insert_place_values(db, cursor, dt_id, user_id):
    """ """

    print("** TABLE place, place_comment, place_description, place_feature_type – INSERT")

    #TODO: appeler le bon DT (et non _output6.xml, uniquement en dev)
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/output6.xml')
    # code du dpt
    dpt = tree.xpath('/DICTIONNAIRE')[0].get('dep')

    # print("INSERT bibl for {0}".format(dt_id))
    insert_bibl(db, cursor, dt_id)
    bibl_id = cursor.lastrowid

    for entry in tree.xpath('/DICTIONNAIRE/article'):
        # stocker les données relatives à chaque Place (article du DT)
        place = {}

        # id de l’article in XML (e.g. 'DT02-00001')
        place['id'] = entry.get('id')

        # code insee (si commune, optionnel)
        place['commune_insee_code'] = entry.xpath('insee')[0].text if entry.xpath('insee') else None

        # code insee de la commune d’appartenance du lieu (ie. code de la commune dans le champ localisation)
        place['localization_commune_insee_code'] = entry.xpath('definition/localisation/commune')[0].get('insee') \
            if entry.xpath('definition/localisation/commune') and place['commune_insee_code'] is None \
            else None
        # TODO: déprécié? supprimer? voir avec CF
        control_vals = ['too_many_insee_codes', 'article_not_found', 'commune_is_empty']
        if place['localization_commune_insee_code'] in control_vals:
            place['localization_commune_insee_code'] = None

        # @precision: relation entre le lieu (place_id) et la commune de localisation (localization_commune_insee_code)
        #   'certain: lieu situé dans la commune, http://vocab.getty.edu/ontology#anchor-28390563
        #   'approximatif': lieu situé près de la commune, http://vocab.getty.edu/ontology#anchor1075244680
        #   absence de @precision: cas impossible à trancher -> tgn3000_related_to ?
        # TODO: des cas où @precision n’est pas renseigné : comment définir le type de relation? voir avec CF
        localization_commune_relation_type = entry.xpath('definition/localisation/commune')[0].get('precision') \
            if entry.xpath('definition/localisation/commune') and place['localization_commune_insee_code'] is not None \
            else None
        # le lieu est dans les environs de la commune
        if localization_commune_relation_type == 'approximatif':
            place['localization_commune_relation_type'] = 'tgn3000_related_to'
        # le lieu est localisé dans la commune
        elif localization_commune_relation_type == 'certain':
            place['localization_commune_relation_type'] = 'broaderPartitive'
        else:
            place['localization_commune_relation_type'] = None

        # formatage de place_description.content (xml_dt:definition)
        # TODO: typer les html5:a ? – pour distinguer les liens à venir vers les FT et les codes insee des communes
        # TODO: pour les communes, inscrire le code insee ou le place_id ?
        # TODO: quid des renvois ? pour l’instant on supprime (cf ci-dessous)
        remove_tags = re.compile('</?(definition|localisation|date|renvoi|commune)[^>]*>')
        # on ne matche que les codes insee conformes au motif \[0-9]{5}\
        rename_commune_optag = re.compile('<commune insee="([0-9]{5})"[^>]*>')
        rename_commune_cltag = re.compile('</commune>')
        rename_typo_tag = re.compile('<(/?)typologie[^>]*>')
        if entry.xpath('definition'):
            description = tostring(entry.xpath('definition')[0], encoding='unicode')
            description = ' '.join(description.split())
            # ATTENTION à l’ordre des replace !!! (on réécrit commune avant de la supprimer…)
            description = re.sub(rename_commune_optag, '<a href="\\1">', description)
            description = re.sub(rename_commune_cltag, '</a>', description)
            description = re.sub(rename_typo_tag, '<\\1a>', description)
            description = re.sub(remove_tags, '', description)
            # Tristesse de découvrir que le schéma n’est respecté… et hacks honteux
            # des small-caps dans les descriptions
            description = re.sub(re.compile('<sm>([^<]+)</sm>'), '<span class="sc">\\1</span>', description)
            # erreurs de segmentation dans la source XML
            description = description.replace('</span> <sup>', '</span><sup>')
            # sortir les sauts de page
            description = re.sub(re.compile('<pg>[0-9]+</pg>'), '', description)
            # des références…
            description = re.sub(re.compile('<(/?)reference>'), '<\\1cite>', description)
            # uppercase first letter of description (bien compliqué…)
            re_first_letter = re.compile('(<a>)?([^ ])')
            first_letter_pos = re.match(re_first_letter, description).start(2)
            description = ''.join([description[:first_letter_pos],
                            description[first_letter_pos].upper(),
                            description[first_letter_pos + 1:]])
        else:
            description = None

        # Validation HTM5, sortie d’une erreur sinon
        description_authorized_tags_set = {'p', 'a', 'i', 'sup', 'span', 'cite'}
        if description is not None:
            html_snippet_validator(description, place['id'], description_authorized_tags_set)

        # TODO: on charge la description même si elle n’est pas valide ?
        place['description'] = description

        # id du département
        place['dpt'] = dpt

        # page de début
        place['num_start_page'] = entry.get('pg')

        # VEDETTE (place.label)
        """
        2020-07: choix d’abandonner la distinction entre vedette pricipale et vedettes secondaires (alt_label)
        place['label'] = entry.xpath('vedette/sm[1]')[0].text.rstrip(',')
        place['label'] = place['label'].strip()
        place['label'] = place['label'].replace('*', '')
        # les vedettes secondaires (optionnel, mais fréquent)
        place['alt_labels'] = []
        for i in entry.xpath('vedette//sm[position()>1]'):
            place['alt_labels'].append(i.text.rstrip(','))
        """
        place['label'] = tostring(entry.xpath('vedette')[0], method='text', encoding='unicode')
        # TODO: vérifier toutes les ponctuations en fin de vedette/label (pour tout supprimer)
        place['label'] = place['label'].strip().rstrip('.,;')
        # SN: le prefixe "*" marque les formes reconstituées/hypothétiques pour les lieux disparus. On supprime ?
        # parfois à la fin de la vedette (cf DT72)
        place['label'] = place['label'].replace('*', '')

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
        # TODO: voir avec JP si on inscrit le commentaire dans <article>
        # TODO: quid des <dfn> pour les formes anciennes2 ?
        commentaire2html = io.StringIO('''\
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:output method="text"/>
                <xsl:template match="/">
                    <xsl:apply-templates/>
                </xsl:template>
                <xsl:template match="pg"/>
                <xsl:template match="p">
                    <xsl:text>&lt;p></xsl:text>
                    <xsl:apply-templates/>
                    <xsl:text>&lt;/p></xsl:text>
                </xsl:template>
                <xsl:template match="forme_ancienne2">
                    <xsl:apply-templates/>
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

                # Validation HTML5 (on se contente de tester, on insère tout de même en base)
                comment_authorized_tags_set = {'p', 'a', 'i', 'sup', 'span', 'cite', 'time'}
                if description is not None:
                    html_snippet_validator(place['comment'], place['id'], comment_authorized_tags_set)
        else:
            place['comment'] = None


        # INSERTIONS

        # bibl, voir plus haut, avant de boucler sur la source XML

        # responsablilty
        creation_date = datetime.now().isoformat(timespec='seconds')
        try:
            cursor.execute(
                "INSERT INTO responsibility ("
                    "user_id,"
                    "bibl_id,"
                    "num_start_page,"
                    "creation_date)"
                "VALUES (?, ?, ?, ?)",
                    (user_id,
                     bibl_id,
                     place['num_start_page'],
                     creation_date))
        except sqlite3.IntegrityError as e:
            print(e, "insert responsability, place %s" % (place['id']))
        responsability_id = cursor.lastrowid
        db.commit()

        # place
        try:
            cursor.execute(
                "INSERT INTO place ("
                    "place_id,"
                    "label,"
                    "country,"
                    "dpt,"
                    "commune_insee_code,"
                    "localization_commune_insee_code,"
                    "localization_commune_relation_type,"
                    "responsibility_id)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (place['id'],
                     place['label'],
                     'FR',
                     place['dpt'],
                     place['commune_insee_code'],
                     place['localization_commune_insee_code'],
                     place['localization_commune_relation_type'],
                     responsability_id))
        except sqlite3.IntegrityError as e:
            print(e, "insert place, place %s" % (place['id']))
        db.commit()

        """ 2020-07: abandon de l’insertion des alt_label
        # place_alt_label
        if place['alt_labels']:
            for alt_label in place['alt_labels']:
                cursor.execute(
                    "INSERT INTO place_alt_label ("
                        "label,"
                        "responsibility_id,"
                        "place_id)"
                    "VALUES (?, ?, ?)",
                        (alt_label,
                         responsability_id,
                         place['id']))
                db.commit()
        """

        # place_comment
        if place['comment']:
            try:
                cursor.execute(
                    "INSERT INTO place_comment ("
                        "content,"
                        "responsibility_id,"
                        "place_id)"
                    "VALUES (?, ?, ?);",
                        (place['comment'],
                         responsability_id,
                         place['id']))
            except sqlite3.IntegrityError as e:
                print(e, "insert place_comment, place %s" % (place['id']))
            db.commit()

        # place_description
        if place['description']:
            try:
                cursor.execute(
                    "INSERT INTO place_description ("
                        "content,"
                        "responsibility_id,"
                        "place_id)"
                    "VALUES (?, ?, ?);",
                        (place['description'],
                         responsability_id,
                         place['id']))
            except sqlite3.IntegrityError as e:
                print(e, "insert place_description, place %s" % (place['id']))
            db.commit()

        # place_feature_type
        if place['feature_types']:
            for feature_type in place['feature_types']:
                try:
                    cursor.execute(
                        "INSERT INTO place_feature_type ("
                            "term,"
                            "responsibility_id,"
                            "place_id)"
                        "VALUES (?, ?, ?);",
                            (feature_type,
                             responsability_id,
                             place['id']))
                except sqlite3.IntegrityError as e:
                    print(e, ("insert place_feature_type: place %s – FT '%s'" % (place['id'], feature_type)))
                db.commit()


# Enregistrer le place_id de la commune de localisation dans place.localization_place_id
# Déprécié, depuis la suppression de place.localization_place_id du modèle
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
    # TODO: appeler le bon DT (et non _output6.xml, uniquement en dev)
    tree = etree.parse('../../../dico-topo/data/'+dt_id+'/output6.xml')
    # tree = etree.parse('../../../dico-topo/data/'+dt_id+'/'+dt_id+'.xml')

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
            <xsl:template match="pg"/>
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

        # récupérer la mention de responsabilité attachée à la création du lieu
        cursor.execute("SELECT responsibility_id FROM place WHERE place_id = '%s'" % place['id'])
        responsibility_id = cursor.fetchone()[0]

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
        #   * dfn
        #       la/les forme(s) d’une entrée forme ancienne, en HTML
        #       Inter <dfn>Estran</dfn> et <dfn>Abugniez</dfn> et <dfn>Gerigniez</dfn>
        #   * rich_ref
        #       la référence d’une entrée forme ancienne avec enrichissement typo, en HTML
        #       cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36
        #   * rich_date
        #       la date avec enrichissement typo, en HTML
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

                # Date des formes anciennes
                # Parfois plusieurs dates pour une forme ancienne ; on n’inscrit en base que la première (cf XLST).
                # Attention au mauvais formatage des dates dans les XML (des sauts de lignes intempestifs…)
                rich_date = str(transform_old_label2rich_date(tree)).lstrip()
                date = re.sub(tags, '', rich_date)
                # remove multiple spaces
                date = " ".join(date.split())
                date = date2iso(date)

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
                            "rich_label,"
                            "rich_date,"
                            "text_date,"
                            "rich_reference,"
                            "rich_label_node,"
                            "responsibility_id,"
                            "place_id)"
                        "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (old_label_id,
                             dfn,
                             rich_date,
                             date,
                             rich_ref,
                             old_label_html_str,
                             responsibility_id,
                             place['id']))
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

