from app.api.feature_type.facade import FeatureTypeFacade
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade
from app.api.placename.facade import PlacenameFacade, PlacenameSearchFacade, PlacenameMapFacade
from app.api.placename_alt_label.facade import PlacenameAltLabelFacade
from app.api.placename_old_label.facade import PlacenameOldLabelFacade, PlacenameOldLabelSearchFacade, \
    PlacenameOldLabelMapFacade
from app.models import Placename, PlacenameOldLabel, InseeCommune, InseeRef, FeatureType, PlacenameAltLabel


class JSONAPIFacadeManager(object):

    FACADE_TYPES = ("default", "search", "map")

    IDMapper = {
        InseeRef.__tablename__: {
            "default": lambda id: "DEP_%s" % id,
            "department": lambda id: "DEP_%s" % id
        },
    }

    FACADES = {
        Placename.__name__: {
            "default": PlacenameFacade,
            "search": PlacenameSearchFacade,
            "map": PlacenameMapFacade
        },
        InseeCommune.__name__: {
            "default": CommuneFacade,
            "search": CommuneFacade,
            "map": CommuneFacade
        },
        PlacenameAltLabel.__name__: {
            "default": PlacenameAltLabelFacade,
            "search": PlacenameAltLabelFacade,
            "map": PlacenameAltLabelFacade
        },
        PlacenameOldLabel.__name__: {
            "default": PlacenameOldLabelFacade,
            "search": PlacenameOldLabelSearchFacade,
            "map": PlacenameOldLabelMapFacade
        },
        InseeRef.__name__: {
            "default": InseeRefFacade,
            "search": InseeRefFacade,
            "map": InseeRefFacade,
        },
        FeatureType.__name__: {
            "default": FeatureTypeFacade,
            "search": FeatureTypeFacade,
            "map": FeatureTypeFacade
        },
    }

    @staticmethod
    def get_facade_class(obj, facade_type):
        try:
            return JSONAPIFacadeManager.FACADES[obj.__class__.__name__][facade_type]
        except KeyError as e:
            print("Facade %s %s unknown" % (obj.__class__.__name__, facade_type))
            return None
