from django.views import View

from vectortiles.mapbox.mixins import MapboxBaseVectorTile
from vectortiles.mixins import BaseVectorTileView


class MVTView(BaseVectorTileView, MapboxBaseVectorTile, View):
    pass
