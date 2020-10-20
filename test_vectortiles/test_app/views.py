from django.views.generic import ListView, DetailView

from test_vectortiles.test_app.models import Feature, Layer
from vectortiles.mapbox.views import MapboxVectorTileVew
from vectortiles.mixins import BaseVectorTileView
from vectortiles.postgis.views import PostgisVectorTileView

# test at feature level and at layer level


class MapboxFeatureView(MapboxVectorTileVew, ListView):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )


class MapboxLayerView(MapboxVectorTileVew, DetailView):
    model = Layer
    vector_tile_fields = ('name', )

    def get_vector_tile_layer_name(self):
        return self.get_object().name

    def get_vector_tile_queryset(self):
        return self.get_object().features.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return BaseVectorTileView.get(self, request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


class PostGISFeatureView(PostgisVectorTileView, ListView):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )


class PostGISLayerView(PostgisVectorTileView, DetailView):
    model = Layer
    vector_tile_fields = ('name', )

    def get_vector_tile_layer_name(self):
        return self.get_object().name

    def get_vector_tile_queryset(self):
        return self.get_object().features.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return BaseVectorTileView.get(self, request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))
