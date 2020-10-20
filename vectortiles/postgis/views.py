from django.views import View

from vectortiles.postgis.mixins import PostgisBaseVectorTile
from vectortiles.mixins import BaseVectorTileView


class PostgisVectorTileView(BaseVectorTileView, PostgisBaseVectorTile, View):
    content_type = "application/x-protobuf"
