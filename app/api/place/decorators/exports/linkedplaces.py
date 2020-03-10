import copy
import json
import os

from flask import url_for, current_app

from app.api.abstract_facade import JSONAPIAbstractFacade
from app.models import InseeCommune, Place

dir_path = os.path.dirname(os.path.realpath(__file__))
templates = {}


def addLink(id):
    return {"type": "closeMatch", "identifer": id}


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


def export_place_to_linkedplace(request, input_data):
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
    for place_jsonapi in input_data["data"]:

        p = Place.query.filter(Place.id == place_jsonapi["id"]).first()
        if not p:
            print("WARNING: place %s not found in db" % place_jsonapi["id"])
            continue

        place_f, _, _ = JSONAPIAbstractFacade.get_facade(url_prefix, p)
        resource = place_f.resource

        feature = from_template('Feature.json')
        feature["@id"] = resource["links"]["self"]  # '""{0}/places/{1}".format(frontend_url, resource["id"])
        feature["properties"]["title"] = resource["attributes"]["label"]
        feature["properties"]["ccodes"] = [resource["attributes"]["country"]]

        if resource["attributes"]["desc"] and len(resource["attributes"]["desc"]) > 0:
            feature["descriptions"] = [
                {
                    "@id": feature["@id"],  # input_data["links"]["self"].split('?')[0],
                    "value": resource["attributes"]["desc"],
                    "lang": "fr"
                }
            ]

        insee_code = resource["attributes"]["localization-insee-code"]
        if insee_code:
            if place_f.obj.commune:
                co = place_f.obj.commune
            else:
                co = place_f.obj.localization_commune
        else:
            co = None

        geometry_collection = from_template('GeometryCollection.json')
        feature["geometry"] = geometry_collection

        # geometry
        if insee_code:
            commune = InseeCommune.query.filter(InseeCommune.id == insee_code).first()
            if commune and commune.longlat:
                point = from_template('Point.json')
                long, lat = commune.longlat.replace("(", "").replace(")", "").split(",")
                point["coordinates"] = [float(long), float(lat)]
                point["geo_wkt"] = "POINT({0} {1})".format(float(long), float(lat))
                point["src"] = "http://id.insee.fr/geo/commune/{0}".format(insee_code)
                point["when"] = {
                    "timespans": [
                        {"start": {"in": "2011"}, "end": {"in": "2011"}},
                    ]
                }
                geometry_collection["geometries"].append(point)

        if len(geometry_collection["geometries"]) == 0:
            feature.pop("geometry")

        # old labels
        old_labels = place_f.obj.old_labels
        if len(old_labels) > 0:
            start_in = sorted([ol.text_date for ol in old_labels if ol.text_date])
            if len(start_in) > 0:
                earliest = start_in[0]
                latest = start_in[-1]
                start = {"earliest": earliest}
                if latest != earliest:
                    start["latest"] = latest
                    assert latest > earliest
                feature["when"] = {
                    "timespans": [
                        {"start": start},
                    ]
                }

            for old_label in old_labels:
                name = from_template('Toponym.json')
                name["toponym"] = old_label.rich_label
                if old_label.rich_reference is not None and len(old_label.rich_reference) > 0:
                    name["citations"] = [{
                        "@id": None,
                        "label": old_label.rich_reference
                    }]
                if old_label.text_date and len(old_label.text_date) > 0:
                    name["when"] = {
                        "timespans": [
                            {"start": {"earliest": old_label.text_date}}
                        ]
                    }
                feature["names"].append(name)

        # feature types
        for ftype in place_f.obj.feature_types:
            if ftype.term:
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
                    # "when": {"timespans": []}
                })
            if co.departement:
                feature["relations"].append({
                    "relationType": "gvp:broaderPartitive",
                    "relationTo": "http://id.insee.fr/geo/departement/{0}".format(co.departement.insee_code),
                    "label": "département de {0}".format(addPrefix(co.departement.label)),
                    # "when": {"timespans": []}
                })
            # need proper ids
            # if co.arrondissement:
            #    feature["relations"].append({
            #        "relationType": "gvp:broaderPartitive",
            #        "relationTo": "http://id.insee.fr/geo/arrondissement/{0}".format(co.arrondissement.insee_code)
            #    })
            # if co.canton:
            #    feature["relations"].append({
            #        "relationType": "gvp:broaderPartitive",
            #        "relationTo": "http://id.insee.fr/geo/canton/{0}".format(co.canton.insee_code)
            #    })

        ## subcommunal linked places
        if len(place_f.obj.linked_places) > 0:
            for lp in place_f.obj.linked_places:
                lp_f, _, _ = JSONAPIAbstractFacade.get_facade(url_prefix, lp)

                feature["relations"].append({
                    "relationType": "gvp:tgn3000_related_to",
                    "relationTo": lp_f.self_link,
                    "label": lp_f.resource["attributes"]["label"],
                    # "when": {"timespans": []}
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


def export_place_to_inline_linkedplace(request, input_data):
    exp, _, _, _ = export_place_to_linkedplace(request, input_data)
    filename = "/tmp/feat.json"

    num_page = 1 if "page[number]" not in request.args else request.args["page[number]"]
    output = "/tmp/inlined-feats.{0}.json".format(num_page)

    try:
        os.remove(output)
    except Exception as e:
        pass

    for i, feat in enumerate(exp["features"]):
        with open(filename, "w", encoding='utf-8') as jsonfile:
            json.dump(feat, jsonfile, ensure_ascii=False)

        code = os.system('jq -c . {0} >> {1}'.format(filename, output))
        print(i, code)

    with open(output, "r", encoding='utf-8') as inlined:
        print(len(exp["features"]))
        return inlined.read(), 200, {}, "text/plain"
