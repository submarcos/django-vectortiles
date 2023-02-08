from rest_framework import renderers

from vectortiles import settings as app_settings


class MVTRenderer(renderers.BaseRenderer):
    media_type = app_settings.VECTOR_TILES_CONTENT_TYPE
    format = app_settings.VECTOR_TILES_EXTENSION

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
