import MySQLdb
from lxml import etree
from lxml.etree import tostring
import re
import io

# TODO: des renvois ? cf ancienne DB

# Ouverture de la connection
db = MySQLdb.connect("localhost","root","rootroot","dicotopo" )
db.set_character_set('utf8')
cursor = db.cursor()
cursor.execute('SET NAMES UTF8MB4;')
cursor.execute('SET CHARACTER SET UTF8MB4;')
cursor.execute('SET character_set_connection=UTF8MB4;')

insee_pattern = re.compile('[0-9]{5}')
tags = re.compile('<[^>]+>')

tree = etree.parse("../dico-topo/data/DT02/DT02.xml")
# on enregistre le code du dpt
dpt = tree.xpath("/DICTIONNAIRE")[0].get("dep")

# TEST SUR ROOT
# f = io.StringIO('''\
#     <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
#         <xsl:template match="/">
#             <foo><xsl:apply-templates select="//article"/></foo>
#         </xsl:template>
#         <xsl:template match="article">
#             <xsl:text>.</xsl:text>
#         </xsl:template>
#     </xsl:stylesheet>''')
# xslt_doc = etree.parse(f)
# transform = etree.XSLT(xslt_doc)
# result = transform(tree)


# conversion HTML5 de toute l’entrée forme_ancienne
oldorth2html = io.StringIO('''\
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
xslt_oldorth2html = etree.parse(oldorth2html)
transform_oldorth2html = etree.XSLT(xslt_oldorth2html)
# nettoyage typo, réutilisable
clean_start = re.compile('^[— ]+')
clean_end = re.compile('[— .,;]+$')
clean_markup = re.compile(',(</[^>]+>)') # sortir la virgule du markup (span, cite, dfn, ?) ; voir si on sort d’autres ponctuations


# utilitaires pour extraire et nettoyer les formes anciennes
get_old_orth = io.StringIO('''\
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
xslt_get_old_orth = etree.parse(get_old_orth)
transform_oldorth2dfn = etree.XSLT(xslt_get_old_orth)

get_old_orth_rich_date = io.StringIO('''\
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
xslt_get_old_orth_rich_date = etree.parse(get_old_orth_rich_date)
transform_oldorth2rich_date = etree.XSLT(xslt_get_old_orth_rich_date)

get_old_orth_rich_ref = io.StringIO('''\
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
xslt_get_old_orth_rich_ref = etree.parse(get_old_orth_rich_ref)
transform_oldorth2rich_ref = etree.XSLT(xslt_get_old_orth_rich_ref)

i = 0
for entry in tree.xpath("/DICTIONNAIRE/article"):
    # un dictionnaire pour stocker les données relative à chaque article
    art = {}
    # id de l’article
    art["id"] = entry.get("id")

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
    #   * old_orth_id           identifiant calculé de la forme ancienne                                        DT02-00043-03
    #   * old_orth_xml_str      élément <forme_ancienne> dans la source XML                                     <forme_ancienne>Inter <i>Estran</i> et <i>Abugniez</i> et <i>Gerigniez,</i> <date>1168</date> <reference>(cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36)</reference>.</forme_ancienne>
    #   * old_orth_html_str     élément <forme_ancienne> converti en HTML                                       <p>Inter <dfn>Estran</dfn> et <dfn>Abugniez</dfn> et <dfn>Gerigniez</dfn>, <time>1168</time> (cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36)</p>
    #   * old_orth_nude_str     élément <forme_ancienne> sans balise                                            Inter Estran et Abugniez et Gerigniez, 1168 (cart. de l’abb. de Thenailles, fos 15, 20, 36)
    #   * dfn                   la/les forme(s) d’une entrée forme ancienne, en HTML                            Inter <dfn>Estran</dfn> et <dfn>Abugniez</dfn> et <dfn>Gerigniez</dfn>
    #   * rich_ref              la référence d’une entrée forme ancienne avec enrichissement typo, en HTML      cart. de l’abb. de Thenailles, f<sup>os</sup> 15, 20, 36
    #   * ref                   la référence d’une entrée forme ancienne sans enrichissement typo               cart. de l’abb. de Thenailles, fos 15, 20, 36
    #   * rich_date             la date avec enrichissement typo, en HTML)                                      <span class="sc">xiii</span><sup>e</sup> siècle (cf DT02-00048-03)
    #   * date                  la date sans enrichissement typo                                                xiiie siècle (idem)
    if entry.xpath("forme_ancienne"):
        n = 1
        for old_orth in entry.xpath("forme_ancienne"):
            old_orth_id = art["id"]+'-0'+str(n) if n < 10 else art["id"]+'-'+str(n)
            old_orth_xml_str = tostring(old_orth, encoding='unicode')
            old_orth_xml_str = " ".join(old_orth_xml_str.split())
            tree = etree.fromstring(old_orth_xml_str)
            # tout le contenu de l’élément forme_ancienne, formaté en HTML
            old_orth_html_str = str(transform_oldorth2html(tree))
            old_orth_html_str = re.sub(clean_start, '', old_orth_html_str)
            old_orth_html_str = re.sub(clean_markup, '\\1,', old_orth_html_str) # sortir les virgules des balises
            old_orth_html_str = re.sub(clean_end, '', old_orth_html_str)
            old_orth_html_str = "<p>%s</p>" % (old_orth_html_str) # on encapsule dans un <p> ? dans <li> ? Todo: à (re)voir
            # tout le contenu de l’élément forme_ancienne, dépouillé des balises
            old_orth_nude_str = re.sub(tags, '', old_orth_html_str)
            # DFN
            # TODO: extraire tous les dfn du champ dans une table dédiée pour indexation
            dfn = str(transform_oldorth2dfn(tree))
            dfn = re.sub(clean_start, '', dfn)
            dfn = dfn.replace(',</dfn>', '</dfn>,') # sortir la ponctuation avant normalisation de la fin de la chaîne
            dfn = re.sub(clean_end, '', dfn)
            # DATE – Attention au mauvais formatage des dates dans les XML (des sauts de lignes intempestifs…)
            # TODO: du code pour normaliser les dates "textuelles"
            rich_date = str(transform_oldorth2rich_date(tree))
            date = re.sub(tags, '', rich_date)
            # print(rich_date + ' = ' + date)
            # Ref (référence de la forme ancienne) ; 1 forme_ancienne avec plus d’une réf ! (pour l’instant, on les vire = choix du prestataire d’ailleurs…)
            # contenu riche : i, sup, pg (on les sort en XSLT), date, sm
            rich_ref = str(transform_oldorth2rich_ref(tree)).strip()
            rich_ref = rich_ref.lstrip('(').rstrip(')') # suppression des parenthèses
            rich_ref = rich_ref.replace(',</cite>', '</cite>,')  # sortir la ponctuation du titre
            ref = re.sub(tags, '', rich_ref)
            n += 1
            i += 1
            cursor.execute(
                "INSERT INTO old_orth"
                "(old_orth_id, entry_id, old_orth,"
                "date_rich, date_nude,"
                "reference_rich, reference_nude,"
                "full_old_orth_html, full_old_orth_nude)"
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (old_orth_id, art['id'], dfn, rich_date, date, rich_ref, ref, old_orth_html_str, old_orth_nude_str))
            db.commit()

    else:
        continue

# Remettre les valeurs vides à NULL… Un peu la honte, mais efficace:
# https://stackoverflow.com/questions/3238319/how-do-i-change-all-empty-strings-to-null-in-a-table
cursor.execute("""
    UPDATE dicotopo.old_orth
    SET
    date_rich = CASE date_rich WHEN '' THEN NULL ELSE date_rich END,
    date_nude = CASE date_nude WHEN '' THEN NULL ELSE date_nude END,
    reference_rich = CASE reference_rich WHEN '' THEN NULL ELSE reference_rich END,
    reference_nude = CASE reference_nude WHEN '' THEN NULL ELSE reference_nude END
""")
db.commit()
db.close()

