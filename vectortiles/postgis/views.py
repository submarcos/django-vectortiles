from django.views import View

from vectortiles.mixins import BaseVectorTileView
from vectortiles.postgis.mixins import PostgisBaseVectorTile


class MVTView(BaseVectorTileView, PostgisBaseVectorTile, View):
    pass
