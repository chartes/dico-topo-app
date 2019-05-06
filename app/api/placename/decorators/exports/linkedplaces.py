import copy
import json
import os

from flask import url_for, current_app

from app.api.abstract_facade import JSONAPIAbstractFacade
from app.models import InseeCommune, Placename

dir_path = os.path.dirname(os.path.realpath(__file__))
templates = {}


def addLink(id):
    return {"type": "exactMatch", "identifer": id}

def addPrefix(name):
    if name[0].lower() in 'aeiouyïäâëüûôöéèê':
        return "l'{0}".format(name)
    else:
        return name

def from_template(fn):
    if fn not in templates:
        with open(os.path.join(dir_path, 'templates', fn), 'r') as f:
            templates[fn] = json.load(f)
    return copy.deepcopy(templates[fn])


def export_placename_to_linkedplace(request, input_data):
    """
    Demonstration of the export feature.
    :param data:
    :return:
    """
    url_prefix = request.host_url[:-1] + current_app.api_url_registrar.url_prefix


    feature_collection = from_template('FeatureCollection.json')

    # so you can work with single data the same way you would with a list
    if not isinstance(input_data["data"], list):
        input_data["data"] = [input_data["data"]]

    # just converting the incoming jsonapi data into a simpler json format of my own
    for placename_jsonapi in input_data["data"]:

        p = Placename.query.filter(Placename.id == placename_jsonapi["id"]).first()
        placename_f, _, _ = JSONAPIAbstractFacade.get_facade(url_prefix, p)
        resource = placename_f.resource

        feature = from_template('Feature.json')
        feature["@id"] = url_for('app_bp.get_placename', placename_id=resource["id"], _external=True)
        feature["properties"]["title"] = resource["attributes"]["label"]
        feature["properties"]["ccode"] = resource["attributes"]["country"]
        feature["descriptions"] = [
            {
                "@id": input_data["links"]["self"].split('?')[0],
                "value": resource["attributes"]["desc"],
                "lang": "fr"
            }
        ]

        geometry_collection = from_template('GeometryCollection.json')
        feature["geometry"] = geometry_collection

        insee_code = resource["attributes"]["localization-insee-code"]
        if insee_code:
            if placename_f.obj.commune:
                co = placename_f.obj.commune
            else:
                co = placename_f.obj.localization_commune
        else:
            co = None
        # geometry
        if insee_code:
            commune = InseeCommune.query.filter(InseeCommune.id == insee_code).first()
            if commune:
                point = from_template('Point.json')
                long, lat = commune.longlat.replace("(", "").replace(")", "").split(",")
                point["coordinates"] = [float(long), float(lat)]
                point["geo_wkt"] = "POINT({0} {1})".format(float(long), float(lat))
                point["src"] = "http://id.insee.fr/geo/commune/{0}".format(insee_code)
                point["when"] = {
                    "timespans": [
                        {"start": {"in": 2011}},
                        {"end": {"in": 2011}}
                    ]
                }
                geometry_collection["geometries"].append(point)

        # old labels
        old_labels = placename_f.obj.old_labels
        if len(old_labels) > 0:
            start_in = sorted([ol.text_date for ol in old_labels if ol.text_date])[0]
            feature["when"] = {
                "timespans": [
                    {"start": {"in": start_in}},
                    {"end": {"in": None}}
                ]
            }

            for old_label in old_labels:
                name = from_template('Toponym.json')
                name["toponym"] = old_label.rich_label
                name["citation"]["label"] = old_label.rich_reference
                name["when"] = {
                    "timespans": [
                        {"start": {"in": old_label.text_date}},
                        {"end": {"in": None}}
                    ]
                }
                feature["names"].append(name)

        # feature types
        for ftype in placename_f.obj.feature_types:
            feature_type = {
                "label": ftype.term
            }
            feature["types"].append(feature_type)

        # relations
        ## administrative hierarchy
        if insee_code:
            if co.region:
                feature["relations"].append({
                    "relationType": "gvp:broaderPartitive",
                    "relationTo": "http://id.insee.fr/geo/region/{0}".format(co.region.insee_code),
                    "label": "région de {0}".format(addPrefix(co.region.label)),
                    "when": {"timespans": []}
                })
            if co.departement:
                feature["relations"].append({
                    "relationType": "gvp:broaderPartitive",
                    "relationTo": "http://id.insee.fr/geo/departement/{0}".format(co.departement.insee_code),
                    "label": "département de {0}".format(addPrefix(co.departement.label)),
                    "when": {"timespans": []}
                })
            # need proper ids
            #if co.arrondissement:
            #    feature["relations"].append({
            #        "relationType": "gvp:broaderPartitive",
            #        "relationTo": "http://id.insee.fr/geo/arrondissement/{0}".format(co.arrondissement.insee_code)
            #    })
            #if co.canton:
            #    feature["relations"].append({
            #        "relationType": "gvp:broaderPartitive",
            #        "relationTo": "http://id.insee.fr/geo/canton/{0}".format(co.canton.insee_code)
            #    })

        ## subcommunal linked places
        if len(placename_f.obj.linked_placenames) > 0:
            for lp in placename_f.obj.linked_placenames:
                lp_f, _, _ = JSONAPIAbstractFacade.get_facade(url_prefix, lp)

                feature["relations"].append({
                    "relationType": "gvp:tgn3000_related_to",
                    "relationTo": lp_f.self_link,
                    "label": lp_f.resource["attributes"]["label"],
                    "when": {"timespans": []}
                })

        # links
        if insee_code:
            feature["links"].append(
                addLink("http://id.insee.fr/geo/commune/{0}".format(insee_code))
            )

            if co.geoname_id:
                feature["links"].append(
                    addLink("http://geonames.org/{0}".format(co.geoname_id))
                )
            if co.databnf_ark:
                feature["links"].append(
                    addLink("https://data.bnf.fr/{0}".format(co.databnf_ark))
                )

            if co.wikidata_item_id:
                feature["links"].append(
                    addLink("https://www.wikidata.org/wiki/{0}".format(co.wikidata_item_id))
                )

            if co.wikipedia_url:
                feature["links"].append(
                    addLink("{0}".format(co.wikipedia_url))
                )

            if co.viaf_id:
                feature["links"].append(
                    addLink("https://viaf.org/viaf/{0}".format(co.viaf_id))
                )

        feature_collection["features"].append(feature)

    return feature_collection, 200, {}, "application/json"


