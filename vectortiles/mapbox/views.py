from django.views import View

from vectortiles.mixins import BaseVectorTileView
from vectortiles.mapbox.mixins import MapboxBaseVectorTile


class MapboxVectorTileVew(BaseVectorTileView, MapboxBaseVectorTile, View):
    content_type = "application/vnd.mapbox-vector-tile"
