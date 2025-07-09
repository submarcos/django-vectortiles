=====
Usage
=====

A vector tile is composed of vector layers which represent different kinds of data. Each layer is composed of features.

To start using django-vectortiles, you need GeoDjango models with geometries.

Then, you need to describe how your data will be embedded in tiles.

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


Well, your vector layer is ready. The next step is to create a tile class and a view to serve it.


Simple layer tile view
**********************

.. code-block:: python

    # in your view file
    from your_app.vector_layers import CityVectorLayer
    from your_app.views import MVTView


    class CityTileView(MVTView):
        layer_classes = [CityVectorLayer]  # you can use get_layer_classes method, or directly get_layers instead

    # in your urls file
    from django.urls import path
    from yourapp import views

    urlpatterns = [
        ...
        views.CityTileView.get_url(),  # serve tiles at default /citytileview/<int:z>/<int:x>/<int:y>
        ...
    ]

Multiple layer tile view
************************

As vector tile layer permits it, you can embed multiple layers in your tile.

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
        views.CityAndStateTileView.get_url(),  # serve tiles at default /cityandstatetileview/<int:z>/<int:x>/<int:y>
        # views.CityAndStateTileView.get_url(prefix="tiles")   # serve tiles at /tiles/<int:z>/<int:x>/<int:y>
        ...
    ]

Using TileJSON
**************

It's a good practice to use TileJSON to tell to your map library how to get your tiles and their definition.
django-vectortiles permits that.

TileJSON and tile views share some data, as vector layers definitions. So we need to factorize some things.

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
        views.CityAndStateTileJSON.get_urls(tiles_urls=views.CityAndStateTileView.get_url()),  # serve tilejson at /city-and-states/tiles.json
        ...
    ]

Now you can use your tiles with a map library like MapLibre or Mapbox GL JS, directly with the provided TileJSON.

.. warning::

    By default, it's your browser's URL that will be used to generate tile urls in TileJSON. Take care of Django and SSL configuration (Django settings, web server headers) if you want to generate an URL with https://

.. note::

    If your application is hosted on a server with many workers, and you want to optimize tile loading, you can add several urls in your TileJSON file.

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

    With these settings, each TileJSON file will contain several urls, and your map library will be able to parallel load tiles at time.


More complex multiple layer tile view
*************************************

You can customize the geometry data embedded in your tiles.


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

.. code-block::  html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>MapBox / MapLibre example</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
            }
        </style>
        <link href='https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css' rel='stylesheet'/>
    </head>
    <body>
    <div id="map" style="width: 100%; height: 100vh"></div>
    <script src='https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js'></script>

    <script>
        var map = new maplibregl.Map({
            container: 'map',
            hash: true,
            style: 'https://demotiles.maplibre.org/style.json', // stylesheet location
            center: [1.77, 44.498], // starting position [lng, lat]
            zoom: 8 // starting zoom
        });
        var nav = new maplibregl.NavigationControl({visualizePitch: true});
        map.addControl(nav, 'top-right');
        var scale = new maplibregl.ScaleControl({
            maxWidth: 80,
            unit: 'metric'
        });
        map.addControl(scale);
        map.on('load', function () {
            map.addSource('layers', {
                'type': 'vector',
                'url': '{% url "city-tilejson" %}'
            });
            map.addLayer(
                {
                    'id': 'background2',
                    'type': 'background',
                    'paint': {
                        'background-color': '#F8F4F0',
                    }

                }
            );
            map.addLayer(
                {
                    'id': 'cities',
                    'type': 'line',
                    'filter': ['==', ['geometry-type'], 'Polygon'],
                    'source': 'layers',
                    'source-layer': 'cities',
                    'layout': {
                        'line-cap': 'round',
                        'line-join': 'round'
                    },
                    'paint': {
                        'line-opacity': 0.4,
                        'line-color': '#3636a8',
                        'line-width': 0.5,
                        'line-dasharray': [10, 10]
                    }

                }
            );

            map.addLayer(
                {
                    "id": "city-borders",
                    "type": "symbol",
                    "source": "layers",
                    "source-layer": "cities",
                    "minzoom": 13,
                    "layout": {
                        "symbol-placement": "line",
                        "symbol-spacing": 350,
                        "text-field": "{nom}",
                        "text-font": ["Noto Sans Italic"],
                        "text-letter-spacing": 0.2,
                        "text-max-width": 5,
                        "text-rotation-alignment": "map",
                        "text-size": 10
                    },
                    "paint": {
                        "text-color": "#3636a8",
                        "text-halo-color": "rgba(255,255,255,0.7)",
                        "text-halo-width": 1
                    }
                }
            );
            map.addLayer(
                {
                    "id": "cities_marker",
                    "type": "symbol",
                    "source": "layers",
                    "source-layer": "city-centroids",
                    "minzoom": 10,
                    "maxzoom": 12,
                    "layout": {
                        "symbol-placement": "point",
                        "symbol-spacing": 350,
                        "text-field": "{nom}",
                        "text-font": ["Noto Sans Italic"],
                        "text-letter-spacing": 0.2,
                        "text-max-width": 5,
                        "text-rotation-alignment": "map",
                        "text-size": 14
                    },
                    "paint": {
                        "text-color": "#3636a8",
                        "text-halo-color": "rgba(255,255,255,0.7)",
                        "text-halo-width": 1.5
                    }
                }
            );

            // Create a popup, but don't add it to the map yet.
            var popup = new maplibregl.Popup({
                closeButton: false,
                closeOnClick: false
            });

            map.on('mouseenter', 'cities_marker', function (e) {
                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';
                var coordinates = e.features[0].geometry.coordinates.slice();
                var description = `${e.features[0].properties.name} (${e.features[0].properties.population} hab.)`;

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(coordinates).setHTML(description).addTo(map);
            });

            map.on('mouseleave', 'cities_marker', function () {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });
        }
    );
    </script>
    </body>
    </html>


Cache policy
************