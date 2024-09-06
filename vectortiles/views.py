from django.http import HttpResponse, JsonResponse
from django.views import View

from vectortiles.mixins import BaseTileJSONView, BaseVectorTileView


class TileJSONView(BaseTileJSONView, View):
    tile_url = None

    def get_tile_url(self):
        return self.tile_url

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.get_tilejson(self.get_tile_url()))


class MVTView(BaseVectorTileView, View):
    def get(self, request, z, x, y, *args, **kwargs):
        """
        Handle GET request to serve tile

        :param request:
        :type request: HttpRequest
        :param x: longitude coordinate tile
        :type x: int
        :param y: latitude coordinate tile
        :type y: int
        :param z: zoom level
        :type z: int

        :rtype HTTPResponse
        """
        content, status = self.get_content_status(int(z), int(x), int(y))
        return HttpResponse(content, content_type=self.content_type, status=status)
