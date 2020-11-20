import re

from app.api.place_comment.facade import PlaceCommentFacade, FlatPlaceCommentFacade
from app.api.place_description.facade import PlaceDescriptionFacade, FlatPlaceDescriptionFacade
from app.api.place_feature_type.facade import PlaceFeatureTypeFacade
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade, InseeRefSearchFacade
from app.api.place.facade import PlaceFacade, PlaceSearchFacade, PlaceMapFacade, LinkedPlaceFacade
from app.api.place_old_label.facade import PlaceOldLabelFacade, PlaceOldLabelSearchFacade, \
    PlaceOldLabelMapFacade, FlatPlaceOldLabelFacade
from app.api.bibl.facade import BiblFacade
from app.api.responsibility.facade import ResponsibilityFacade, FlatResponsibilityFacade
from app.api.user.facade import UserFacade
from app.models import Place, PlaceOldLabel, InseeCommune, InseeRef, PlaceFeatureType, Bibl, \
    Responsibility, User, PlaceDescription, PlaceComment


_FACADES = {
    "lp": LinkedPlaceFacade,
    "flat-resp": FlatResponsibilityFacade,
    "flat-place-desc": FlatPlaceDescriptionFacade,
    "flat-place-comment": FlatPlaceCommentFacade,
    "flat-old-label": FlatPlaceOldLabelFacade,

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
    def get_facade_class_from_name(name):
        try:
            return JSONAPIFacadeManager.FACADES[name]
        except Exception as e:
            print(e)
            print("Facade %s %s unknown" % (name))
            return None

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
