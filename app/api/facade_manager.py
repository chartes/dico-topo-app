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
    Place.__tablename__: {
        "default": PlaceFacade,
        "search": PlaceSearchFacade,
        "map": PlaceMapFacade
    },
    InseeCommune.__tablename__: {
        "default": CommuneFacade,
        "search": CommuneFacade,
        "map": CommuneFacade
    },
    PlaceAltLabel.__tablename__: {
        "default": PlaceAltLabelFacade,
        "search": PlaceAltLabelFacade,
        "map": PlaceAltLabelFacade
    },
    PlaceOldLabel.__tablename__: {
        "default": PlaceOldLabelFacade,
        "search": PlaceOldLabelSearchFacade,
        "map": PlaceOldLabelMapFacade
    },
    InseeRef.__tablename__: {
        "default": InseeRefFacade,
        "search": InseeRefSearchFacade,
        "map": InseeRefFacade,
    },
    PlaceFeatureType.__tablename__: {
        "default": PlaceFeatureTypeFacade,
        "search": PlaceFeatureTypeFacade,
        "map": PlaceFeatureTypeFacade
    },
    Bibl.__tablename__: {
        "default": BiblFacade,
        "search": BiblFacade,
        "map": BiblFacade
    },
    Responsibility.__tablename__: {
        "default": ResponsibilityFacade,
        "search": ResponsibilityFacade,
        "map": ResponsibilityFacade
    },
    User.__tablename__: {
        "default": UserFacade,
        "search": UserFacade,
        "map": UserFacade
    },
    PlaceDescription.__tablename__: {
        "default": PlaceDescriptionFacade,
        "search": PlaceDescriptionFacade,
        "map": PlaceDescriptionFacade
    },
    PlaceComment.__tablename__: {
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

    @staticmethod
    def get_facade_class(obj, facade_type="default"):
        try:
            return JSONAPIFacadeManager.FACADES[obj.__tablename__][facade_type]
        except Exception as e:
            print(e)
            print("Facade %s %s unknown" % (obj, facade_type))
            return None

    @staticmethod
    def get_facade_class_from_facade_type(t, facade_type="default"):
        t = t.replace("-", "_")
        try:
            return JSONAPIFacadeManager.FACADES[t][facade_type]
        except Exception as e:
            print("Facade %s %s unknown" % (t, facade_type))
            return None
