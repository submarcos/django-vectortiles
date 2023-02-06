from rest_framework import renderers


class MVTRenderer(renderers.BaseRenderer):
    media_type = "application/vnd.mapbox-vector-tile"
    format = "pbf"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
