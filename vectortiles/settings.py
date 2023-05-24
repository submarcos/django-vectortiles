from django.conf import settings

VECTOR_TILES_CONTENT_TYPE = getattr(
    settings, "VECTOR_TILES_CONTENT_TYPE", "application/vnd.mapbox-vector-tile"
)
VECTOR_TILES_EXTENSION = getattr(settings, "VECTOR_TILES_EXTENSION", "mvt")
VECTOR_TILES_BACKEND = "vectortiles.backends.postgis"  # to use python backend, set to 'vectortiles.backends.python'
VECTOR_TILES_URLS = getattr(settings, "VECTOR_TILES_URLS", None)
