USAGE
=====

A vector tile is composed by vector layers which represent different kind of data. Each layer is composed by features.

To start using django-vectortiles, you need GeoDjango models with geometries.

Then, you need to describe how your data will be embed in tiles.

Start by creating vector layers for your data...

.. code-block:: python
    # in your app models.py
    from django.contrib.gis.db import models


    class City(models.Model):
        name = models.CharField(max_length=250)
        city_code = models.CharField(max_length=10, unique=True)
        population = models.IntegerField(default=0)
        geom = models.MultiPolygonField(srid=4326)


    # in a vector_layers.py file (for example)
    from vectortiles import VectorLayer
    from your_app.models import City


    class CityVectorLayer(VectorLayer):
        model = City  # your model, as django conventions you can use queryset or get_queryset method instead)
        id = "cities"  # layer id in you vector layer. each class attribute can be defined by get_{attribute} method
        tile_fields = ('city_code', "name") # fields to include in tile
        min_zoom = 10 # minimum zoom level to include layer. Take care of this, as it could be a performance issue. Try to not embed data that will no be shown in your style definition.
        # all attributes available in vector layer definition can be defined


Well. your vector layer is ready. next step is to create a tile class and a view to serve it.


Simple layer tile view
**********************

.. code-block:: python

    # in your view file
    from your_app.vector_layers import CityVectorLayer
    from your_app.views import MVTView


    class CityTileView(MVTView):
        layer_classes = [CityVectorLayer, CityCentroidVectorLayer]  # you can use get_layer_classes method, or directly get_layers instead

    # in your urls file
    from django.urls import path
    from yourapp import views

    urlpatterns = [
        ...
        views.CityTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>
        ...
    ]

Multiple layer tile view
************************

As vector tile layer permit it, you can embed multiple layers in your tile.

Let's create a second layer.


.. code-block:: python

    # in your app models.py
    class State(models.Model):
        name = models.CharField(max_length=250)
        state_code = models.CharField(max_length=10, unique=True)
        geom = models.MultiPolygonField(srid=4326)

    # in vector_layers.py file
    class StateVectorLayer(VectorLayer):
        model = State
        id = "states"
        tile_fields = ('state_code', "name")
        min_zoom = 3

    # in your view file
    class CityAndStateTileView(MVTView):
        layer_classes = [CityVectorLayer, StateVectorLayer]

    # in your urls file
    urlpatterns = [
        ...
        views.CityAndStateTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>
        ...
    ]

Using TileJSON
**************

It's a good practice to use tilejson to tell to your map library how to gt your tiles and their defintion.
django-vectortiles permit that.

TileJSON and tile views share some data, as vactor layers definition. So we need to factorize some things.

.. code-block:: python

    # in your view file

    class CityAndStateBaseLayer:
        # mixin for your two views
        layer_classes = [CityVectorLayer, StateVectorLayer]
        prefix_url = 'city-and-states'  # as tilejson need to known tiles URL, we need to define a url prefix for our tiles

    class CityAndStateTileView(CityAndStateBaseLayer, MVTView):
        pass


    class CityAndStateTileJSON(CityAndStateBaseLayer, TileJSONView):
        pass


    # in your urls file
    urlpatterns = [
        ...
        views.CityAndStateTileView.get_url(),  # serve tiles at /city-and-states/<int:z>/<int:x>/<int:y>
        views.CityAndStateTileJSON.get_url(),  # serve tilejson at /city-and-states/tiles.json
        ...
    ]

Now you can use your tiles with a map library like MapLibre or Mapbox GL JS, directly wit hthe tileJSON provided.

.. warning::

    By default, it's your browser URL that will be used to generate tile url in tilejson. Take care about django and SSL configuration (django settings, web server headers) if you want to generate an URL with https://

.. note::

    If your application is hosted on server with many workers, and you want to optimized tile loading, you can add several urls in your tilejson file.

    .. code-block:: python

        # add in your settings.py file
        ALLOWED_HOSTS = [
            "a.tiles.xxxx",
            "b.tiles.xxxx",
            "c.tiles.xxxx",
            ...
        ]

        VECTOR_TILES_URLS = [
            "https://a.tiles.xxxx",
            "https://b.tiles.xxxx",
            "https://c.tiles.xxxx",
        ]

    With these settings, each tilejson file will contain several urls, and your map library will be able to parallel load tiles at time.


More complex multiple layer tile view
*************************************

You can customize geometry data embed in your tiles.


.. code-block:: python

    class CityCentroidVectorLayer(VectorLayer):
        queryset = City.objects.annotate(
            centroid=Centroid("geom"), # compute the city centroïd
            area=Area("geom"), # compute the city area
        )
        geom_field = "centroid"  # use the centroid field as geometry feature
        id = "city_centroids"
        tile_fields = ('name', 'city_code', 'area', 'population')  # add area and population properties in each tile feature
        min_zoom = 7  # let's show city name at zoom 7



Complex related model tile view
*******************************

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
    from your_app.models import Layer


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
    from your_app import views


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
        queryset = Feature.objects.all()
        id = "features"
        tile_fields = ('name', )
        queryset_limit = 100
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
        id = "features"
        tile_fields = ('name', )
        queryset_limit = 100

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
