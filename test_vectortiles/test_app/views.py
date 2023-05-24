from hashlib import md5

from django.core.cache import cache
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from test_vectortiles.test_app.models import Feature, FullDataLayer
from test_vectortiles.test_app.vt_layers import (
    CityCentroidVectorLayer,
    FeatureLayerFilteredByDateVectorLayer,
    FeatureVectorLayer,
    FullDataFeatureVectorLayer,
)
from vectortiles.mixins import BaseVectorTileView
from vectortiles.rest_framework.renderers import MVTRenderer
from vectortiles.rest_framework.views import MVTAPIView

# test at feature level and at layer level
from vectortiles.views import MVTView, TileJSONView


class FeatureVectorLayers:
    layers = [FeatureVectorLayer()]


class FeatureView(FeatureVectorLayers, MVTView):
    """Simple model View"""


class FeatureTileJSONView(FeatureVectorLayers, TileJSONView):
    """Simple model TileJSON View"""

    name = "My feature dataset"
    attribution = "@IGN - BD Topo 12/2022"
    description = "My dataset"


class MultipleVectorLayers:
    def get_layers(self):
        return [
            FullDataFeatureVectorLayer(layer)
            for layer in FullDataLayer.objects.filter(include_in_tilejson=True)
        ] + [CityCentroidVectorLayer()]


class LayerView(MultipleVectorLayers, MVTView):
    """Multiple tiles in same time, each Layer instance is a tile layer"""

    def get_layers_last_update(self):
        last_updated_layer = (
            FullDataLayer.objects.all()
            .order_by("-update_datetime")
            .only("update_datetime")
            .first()
        )
        return last_updated_layer.update_datetime if last_updated_layer else None

    def get_content_status(self, z, x, y):
        cache_key = md5(
            f"tilejson-{self.get_layers_last_update()}-{z}-{x}-{y}".encode()
        ).hexdigest()
        if cache.has_key(cache_key):  # NOQA W601
            tile, status = cache.get(cache_key), 200

        else:
            tile, status = super().get_content_status(z, x, y)
            cache.set(cache_key, tile, timeout=3600 * 24 * 30)
        return tile, status


class LayerTileJSONView(MultipleVectorLayers, TileJSONView):
    """Simple model TileJSON View"""

    name = "My layers dataset"
    attribution = "@IGN - BD Topo 12/2022"
    legend = "https://avatars.githubusercontent.com/u/7448208?s=96&v=4"
    description = "My dataset"
    center = [1.77, 44.498, 8]
    min_zoom = 6
    max_zoom = 18

    def get_tile_url(self):
        return reverse("layer-pattern")


class FeatureWithDateView(MVTView):
    layers = [FeatureLayerFilteredByDateVectorLayer()]


class FeatureAPIView(FeatureVectorLayers, MVTAPIView):
    pass


class FeatureViewSet(BaseVectorTileView, viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    layers = [FeatureVectorLayers()]

    @action(
        detail=False,
        methods=["get"],
        renderer_classes=(MVTRenderer,),
        url_path=r"tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)",
        url_name="tile",
    )
    def tile(self, request, z, x, y, *args, **kwargs):
        z, x, y = int(z), int(x), int(y)
        content, status = self.get_content_status(z, x, y)
        return Response(content, status=status)


class TileJSONFeatureView(TileJSONView):
    name = "Feature tileset"
    description = "feature tileset"
    attribution = "© JEC"

    def get_tile_url(self):
        return reverse("feature-pattern")


class IndexView(TemplateView):
    template_name = "index.html"
