import importlib.metadata

from django.utils.module_loading import import_string

from vectortiles import settings as app_settings

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except:
    __version__ = "unknown"

VectorLayer = import_string(f"{app_settings.VECTOR_TILES_BACKEND}.VectorLayer")
