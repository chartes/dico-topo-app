from app.api.feature_type.facade import FeatureTypeFacade
from app.api.insee_commune.facade import CommuneFacade
from app.api.insee_ref.facade import InseeRefFacade
from app.api.place.facade import PlaceFacade, PlaceSearchFacade, PlaceMapFacade
from app.api.place_alt_label.facade import PlaceAltLabelFacade
from app.api.place_old_label.facade import PlaceOldLabelFacade, PlaceOldLabelSearchFacade, \
    PlaceOldLabelMapFacade
from app.api.bibl.facade import BiblFacade
from app.models import Place, PlaceOldLabel, InseeCommune, InseeRef, FeatureType, PlaceAltLabel, Bibl


class JSONAPIFacadeManager(object):

    FACADE_TYPES = ("default", "search", "map")

    IDMapper = {
        InseeRef.__tablename__: {
            "default": lambda id: id,
            "department": lambda id: "DEP_%s" % id
        },
    }

    FACADES = {
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
            "search": InseeRefFacade,
            "map": InseeRefFacade,
        },
        FeatureType.__name__: {
            "default": FeatureTypeFacade,
            "search": FeatureTypeFacade,
            "map": FeatureTypeFacade
        },
        Bibl.__name__:{
            "default": BiblFacade,
            "search": BiblFacade,
            "map": BiblFacade
        }
    }

    @staticmethod
    def get_facade_class(obj, facade_type):
        try:
            return JSONAPIFacadeManager.FACADES[obj.__class__.__name__][facade_type]
        except KeyError as e:
            print("Facade %s %s unknown" % (obj.__class__.__name__, facade_type))
            return None
