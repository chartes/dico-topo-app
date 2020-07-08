import re

from app.api.place_comment.facade import PlaceCommentFacade
from app.api.place_description.facade import PlaceDescriptionFacade
from app.api.place_feature_type.facade import PlaceFeatureTypeFacade
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade, InseeRefSearchFacade
from app.api.place.facade import PlaceFacade, PlaceSearchFacade, PlaceMapFacade
from app.api.place_alt_label.facade import PlaceAltLabelFacade
from app.api.place_old_label.facade import PlaceOldLabelFacade, PlaceOldLabelSearchFacade, \
    PlaceOldLabelMapFacade
from app.api.bibl.facade import BiblFacade
from app.api.responsibility.facade import ResponsibilityFacade
from app.api.user.facade import UserFacade
from app.models import Place, PlaceOldLabel, InseeCommune, InseeRef, PlaceFeatureType, PlaceAltLabel, Bibl, \
    Responsibility, User, PlaceDescription, PlaceComment


_FACADES = {
    Place.__name__: {
        "default": PlaceFacade,
        "search": PlaceSearchFacade,
        "map": PlaceMapFacade
    },
    InseeCommune.__name__: {
        "default": CommuneFacade,
        "search": CommuneFacade,
        "map": CommuneFacade
    },
    PlaceAltLabel.__name__: {
        "default": PlaceAltLabelFacade,
        "search": PlaceAltLabelFacade,
        "map": PlaceAltLabelFacade
    },
    PlaceOldLabel.__name__: {
        "default": PlaceOldLabelFacade,
        "search": PlaceOldLabelSearchFacade,
        "map": PlaceOldLabelMapFacade
    },
    InseeRef.__name__: {
        "default": InseeRefFacade,
        "search": InseeRefSearchFacade,
        "map": InseeRefFacade,
    },
    PlaceFeatureType.__name__: {
        "default": PlaceFeatureTypeFacade,
        "search": PlaceFeatureTypeFacade,
        "map": PlaceFeatureTypeFacade
    },
    Bibl.__name__: {
        "default": BiblFacade,
        "search": BiblFacade,
        "map": BiblFacade
    },
    Responsibility.__name__: {
        "default": ResponsibilityFacade,
        "search": ResponsibilityFacade,
        "map": ResponsibilityFacade
    },
    User.__name__: {
        "default": UserFacade,
        "search": UserFacade,
        "map": UserFacade
    },
    PlaceDescription.__name__: {
        "default": PlaceDescriptionFacade,
        "search": PlaceDescriptionFacade,
        "map": PlaceDescriptionFacade
    },
    PlaceComment.__name__: {
        "default": PlaceCommentFacade,
        "search": PlaceCommentFacade,
        "map": PlaceCommentFacade
    }
}

class JSONAPIFacadeManager(object):

    FACADE_TYPES = ("default", "search", "map")

    IDMapper = {
        InseeRef.__tablename__: {
            "default": lambda id: id,
            "department": lambda id: "DEP_%s" % id
        },
    }

    FACADES = _FACADES

    IMMEDIATE_FACADES = {
        # transform AbcdDefg to abc_defg : {...}
        "_".join(re.findall('[A-Z][^A-Z]*', f)).lower() : _FACADES[f]
        for f in _FACADES
    }

    @staticmethod
    def get_facade_class(obj, facade_type="default"):
        try:
            return JSONAPIFacadeManager.FACADES[obj.__class__.__tablename__][facade_type]
        except Exception as e:
            try:
                return JSONAPIFacadeManager.IMMEDIATE_FACADES[facade_type]
            except KeyError as e:
                print(e)
            print("Facade %s %s unknown" % (obj, facade_type))
            return None

    @staticmethod
    def get_facade_class_from_facade_type(t, facade_type="default"):
        t = t.replace("-", "_")
        try:
            return JSONAPIFacadeManager.FACADES[t][facade_type]
        except Exception as e:
            try:
                return JSONAPIFacadeManager.IMMEDIATE_FACADES[t][facade_type]
            except KeyError as e:
                print(e)
            print("Facade %s unknown" % t)
            return None
