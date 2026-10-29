from geonode.settings import *  # noqa: F403


INSTALLED_APPS += ("rndt",)  # noqa: F405
LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"
