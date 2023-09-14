USAGE
=====


Simple model view
*****************

.. code-block:: python

    # in your app models.py
    from django.contrib.gis.db import models

    class Feature(models.Model):
        geom = models.GeometryField(srid=4326)
        name = models.CharField(max_length=250)

    # in your view file
    from django.views.generic import ListView
    from vectortiles.postgis.views import MVTView
    from yourapp.models import Feature


    class FeatureTileView(MVTView, ListView):
        model = Feature
        vector_tile_layer_name = "features"  # name for data layer in vector tile
        vector_tile_fields = ('name',)  # model fields or queryset annotates to include in tile
        # vector_tile_content_type = "application/x-protobuf"  # if you want to use custom content_type
        # vector_tile_queryset = None  # define a queryset for your features
        # vector_tile_queryset_limit = None  # as queryset could not be sliced, set here a limit for your features per tile
        # vector_tile_geom_name = "geom"  # geom field to consider in qs
        # vector_tile_extent = 4096  # tile extent
        # vector_tile_buffer = 256  # buffer around tile

    # in your urls file
    from django.urls import path
    from yourapp import views


    urlpatterns = [
        ...
        path('tiles/<int:z>/<int:x>/<int:y>', views.FeatureTileView.as_view(), name="feature-tile"),
        ...
    ]

Related model view
******************

.. code-block:: python

    # in your app models.py
    from django.contrib.gis.db import models


    class Layer(models.Model):
        name = models.CharField(max_length=250)


    class Feature(models.Model):
        geom = models.GeometryField(srid=4326)
        name = models.CharField(max_length=250)
        layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name='features')

    # in your views.py file
    from django.views.generic import DetailView
    from vectortiles.mixins import BaseVectorTileView
    from vectortiles.postgis.views import MVTView
    from yourapp.models import Layer


    class LayerTileView(MVTView, DetailView):
        model = Layer
        tile_fields = ('name', )

        def get_id(self):
            return self.get_object().name

        def get_queryset(self):
            return self.get_object().features.all()

        def get(self, request, *args, **kwargs):
            self.object = self.get_object()
            return BaseVectorTileView.get(self,request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


    # in your urls file
    from django.urls import path
    from yourapp import views


    urlpatterns = [
        ...
        path('layer/<int:pk>/tile/<int:z>/<int:x>/<int:y>', views.LayerTileView.as_view(), name="layer-tile"),
        ...
    ]

Django Rest Framework
*********************

.. code-block:: python

    # in your views.py file
    from vectortiles.rest_framework.renderers import MVTRenderer


    class FeatureAPIView(BaseVectorTile, APIView):
        vector_tile_queryset = Feature.objects.all()
        vector_tile_layer_name = "features"
        vector_tile_fields = ('name', )
        vector_tile_queryset_limit = 100
        renderer_classes = (MVTRenderer, )

        def get(self, request, *args, **kwargs):
            return Response(self.get_tile(kwargs.get('x'), kwargs.get('y'), kwargs.get('z')))

    # in your urls file
    urlpatterns = [
        ...
        path('features/tiles/<int:z>/<int:x>/<int:y>', FeatureAPIView.as_view(),
             name="feature-tile-drf"),
        ...
    ]

    # or extending viewset

    class FeatureViewSet(BaseVectorTile, viewsets.ModelViewSet):
        queryset = Feature.objects.all()
        vector_tile_layer_name = "features"
        vector_tile_fields = ('name', )
        vector_tile_queryset_limit = 100

        @action(detail=False, methods=['get'], renderer_classes=(MVTRenderer, ),
                url_path='tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)', url_name='tile')
        def tile(self, request, *args, **kwargs):
            return Response(self.get_tile(x=int(kwargs.get('x')), y=int(kwargs.get('y')), z=int(kwargs.get('z'))))

    # in your urls file
    router = SimpleRouter()
    router.register(r'features', FeatureViewSet, basename='features')

    urlpatterns += router.urls


then use http://your-domain/features/tiles/{z}/{x}/{y}.pbf

MapLibre Example
****************

.. literalinclude:: ../test_vectortiles/test_app/templates/index.html
   :language: html
