from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from test_vectortiles.test_app.models import Feature, Layer
from vectortiles.mapbox.views import MVTView as MapboxMVTView
from vectortiles.mixins import BaseVectorTileView, VectorLayer
from vectortiles.postgis.mixins import PostgisBaseVectorTile
from vectortiles.postgis.views import MVTView as PostgisMVTView
from vectortiles.rest_framework.renderers import MVTRenderer

# test at feature level and at layer level
from vectortiles.views import TileJSONView


class MapboxFeatureView(MapboxMVTView, ListView):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )
    vector_tile_queryset_limit = 100


class MapboxLayerView(MapboxMVTView, DetailView):
    model = Layer
    vector_tile_fields = ('name', )

    def get_vector_tile_layer_name(self):
        return self.get_object().name

    def get_vector_tile_queryset(self):
        return self.get_object().features.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return BaseVectorTileView.get(self, request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


class PostGISFeatureView(PostgisMVTView, ListView):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )
    vector_tile_queryset_limit = 100


class PostGISFeatureViewWithManualVectorTileQuerySet(PostgisMVTView, DetailView):
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )

    def get(self, request, *args, **kwargs):
        self.vector_tile_queryset = Feature.objects.all()

        return BaseVectorTileView.get(self, request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


class PostGISFeatureWithDateView(PostgisMVTView, ListView):
    queryset = Feature.objects.filter(date="2020-07-07")
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )


class PostGISLayerView(PostgisMVTView, DetailView):
    model = Layer
    vector_tile_fields = ('name', )

    def get_vector_tile_layer_name(self):
        return self.get_object().name

    def get_vector_tile_queryset(self):
        return self.get_object().features.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return BaseVectorTileView.get(self, request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


class PostGISDRFFeatureView(PostgisBaseVectorTile, APIView):
    vector_tile_queryset = Feature.objects.all()
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )
    vector_tile_queryset_limit = 100
    renderer_classes = (MVTRenderer, )

    def get(self, request, *args, **kwargs):
        return Response(self.get_tile(kwargs.get('x'), kwargs.get('y'), kwargs.get('z')))


class PostGISDRFFeatureViewSet(PostgisBaseVectorTile, viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    vector_tile_layer_name = "features"
    vector_tile_fields = ('name', )
    vector_tile_queryset_limit = 100

    @action(detail=False, methods=['get'], renderer_classes=(MVTRenderer, ),
            url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)', url_name='tile')
    def tile(self, request, *args, **kwargs):
        return Response(self.get_tile(x=int(kwargs.get('x')), y=int(kwargs.get('y')), z=int(kwargs.get('z'))))


class MapboxTileJSONFeatureView(TileJSONView):
    vector_tile_tilejson_name = "Feature tileset"
    vector_tile_tilejson_description = "generated from mapbox library"
    vector_tile_tilejson_attribution = "© JEC"

    def get_tile_url(self):
        return reverse('feature-mapbox-pattern')

    def get_vector_layers(self):
        return [
            VectorLayer('features', description="Feature layer").get_vector_layer()
        ]


class MapboxTileJSONLayerView(TileJSONView, DetailView):
    vector_tile_tilejson_name = "Layer's features tileset"
    vector_tile_tilejson_description = "generated from mapbox library"
    vector_tile_tilejson_attribution = "© JEC"
    model = Layer

    def get_tile_url(self):
        return reverse('layer-mapbox-pattern', args=(self.kwargs.get('pk'),))

    def get_vector_layers(self):
        return [
            VectorLayer(self.get_object().name, description="Feature layer", ).get_vector_layer()
        ]


class PostGISTileJSONFeatureView(TileJSONView):
    vector_tile_tilejson_name = "Feature tileset"
    vector_tile_tilejson_description = "generated from postgis database"
    vector_tile_tilejson_attribution = "© JEC"

    def get_tile_url(self):
        return reverse('feature-postgis-pattern')

    def get_vector_layers(self):
        return [
            VectorLayer('features', description="Feature layer").get_vector_layer()
        ]


class PostGISTileJSONLayerView(TileJSONView, DetailView):
    model = Layer
    vector_tile_tilejson_name = "Layer's features tileset"
    vector_tile_tilejson_description = "generated from postgis database"
    vector_tile_tilejson_attribution = "© JEC"

    def get_tile_url(self):
        return reverse('layer-postgis-pattern', args=(self.kwargs.get('pk'), ))

    def get_vector_layers(self):
        return [
            VectorLayer(self.get_object().name, description="Feature layer", ).get_vector_layer()
        ]


class IndexView(TemplateView):
    template_name = "index.html"
