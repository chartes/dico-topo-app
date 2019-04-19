import copy
import json
import os

from flask import url_for

from app.api.abstract_facade import JSONAPIAbstractFacade
from app.models import InseeCommune, Placename

dir_path = os.path.dirname(os.path.realpath(__file__))
templates = {}


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
    feature_collection = from_template('FeatureCollection.json')

    # so you can work with single data the same way you would with a list
    if not isinstance(input_data["data"], list):
        input_data["data"] = [input_data["data"]]

    # just converting the incoming jsonapi data into a simpler json format of my own
    for placename_jsonapi in input_data["data"]:

        p = Placename.query.filter(Placename.id == placename_jsonapi["id"]).first()
        placename_f, _, _ = JSONAPIAbstractFacade.get_facade("", p)
        resource = placename_f.resource

        feature = from_template('Feature.json')
        feature["@id"] = url_for('app_bp.get_placename', placename_id=resource["id"], _external=True)
        feature["properties"]["title"] = resource["attributes"]["label"]
        feature["properties"]["ccode"] = resource["attributes"]["country"]

        geometry_collection = from_template('GeometryCollection.json')
        feature["geometry"] = geometry_collection

        insee_code = resource["attributes"]["localization-insee-code"]
        if insee_code:
            commune = InseeCommune.query.filter(InseeCommune.id == insee_code).first()
            if commune:
                point = from_template('Point.json')
                long, lat = commune.longlat.replace("(", "").replace(")", "").split(",")
                point["coordinates"] = [float(long), float(lat)]
                point["geo_wkt"] = "POINT({0} {1})".format(float(long), float(lat))
                point["src"] = "http://id.insee.fr/geo/commune/{0}".format(insee_code)
                # todo : point["when"]
                geometry_collection["geometries"].append(point)

        old_labels = placename_f.obj.old_labels
        if len(old_labels) > 0:
            start_in = sorted([ol.text_date for ol in old_labels])[0]
            feature["when"] = {
                "timespans": {
                    "start": {"in": start_in}
                }
            }

            for old_label in old_labels:
                name = from_template('Toponym.json')
                name["toponym"] = old_label.rich_label
                name["citation"]["label"] = old_label.rich_reference

                feature["names"].append(name)


        # todo : feature["when"]["timespans"]["end"]

        feature_collection["features"].append(feature)

    return feature_collection, 200, {}, "application/json"


