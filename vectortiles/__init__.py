from django.utils.module_loading import import_string

from vectortiles import settings as app_settings

VectorLayer = import_string(f"{app_settings.VECTOR_TILES_BACKEND}.VectorLayer")
