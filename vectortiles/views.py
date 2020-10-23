from django.http import JsonResponse
from django.views import View

from vectortiles.mixins import BaseTileJSONMixin


class TileJSONView(BaseTileJSONMixin, View):
    tile_url = None

    def get_tile_url(self):
        return self.tile_url

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.get_tilejson(self.get_tile_url()))
