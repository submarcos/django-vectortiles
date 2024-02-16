![Tests](https://github.com/submarcos/django-vectortiles/workflows/Python%20/%20Django%20matrix%20test/badge.svg)
[![Coverage](https://codecov.io/gh/submarcos/django-vectortiles/branch/master/graph/badge.svg)](https://codecov.io/gh/submarcos/django-vectortiles)

![Python Version](https://img.shields.io/badge/python-%3E%3D%203.7-blue.svg)
![Django Version](https://img.shields.io/badge/django-%3E%3D%203.2-blue.svg)

# Generate MapBox VectorTiles from GeoDjango models

## Directly with PostgreSQL/PostGIS 2.4+ or python native mapbox_vector_tile

## [Read full documentation](https://django-vectortiles.readthedocs.io/)

### Installation

#### Basic
```bash
pip install django-vectortiles
```

* By default, postgis backend is enabled.
* Ensure you have psycopg installed

#### If you don't want to use Postgis and / or PostgreSQL
```bash
pip install django-vectortiles[python]
```
* This will include mapbox_vector_tiles package and its dependencies
* Set ```VECTOR_TILES_BACKEND="vectortiles.backends.python"``` in your project settings.

### Examples

Let's create vector tiles with your city geometries.

* assuming you have ```django.contrib.gis``` in your ```INSTALLED_APPS``` and a gis compatible database backend

```python
# in your app models.py

from django.contrib.gis.db import models


class City(models.Model):
    name = models.CharField(max_length=250)
    city_code = models.CharField(max_length=10, unique=True)
    population = models.IntegerField(default=0)
    geom = models.MultiPolygonField(srid=4326)
```


#### Simple Example:

```python
from yourapp.models import City

# in a vector_layers.py file
from vectortiles import VectorLayer


class CityVL(VectorLayer):
    model = City
    id = "cities"  # layer id / name in tile
    tile_fields = ("name", "city_code")  # add name and city_code properties in each tile feature
    min_zoom = 9  # don't embed city borders at low zoom levels

# in your view file

from yourapp.vector_layers import CityVL

from vectortiles.views import MVTView


class CityTileView(MVTView):
    layer_classes = [CityVL]


# in your urls file
from django.urls import path
from yourapp import views

urlpatterns = [
    ...
    CityTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>. You can override url prefix and tile scheme in class attributes.
    ...
]
```
#### Example with multiple layers

Suppose you want to make a map with your city borders, and a point in each city center that shows a popup with city name, population an area.

```python
from django.contrib.gis.db.models.functions import Centroid, Area
from yourapp.models import City

# in a vector_layers.py file
from vectortiles import VectorLayer


class CityVectorLayer(VectorLayer):
    model = City
    id = "cities"
    tile_fields = ('city_code', "name")
    min_zoom = 10

    
class CityCentroidVectorLayer(VectorLayer):
    queryset = City.objects.annotate(
        centroid=Centroid("geom"), # compute the city centroïd
        area=Area("geom"), # compute the city centroïd
    )  
    geom_field = "centroid"  # use the centroid field as geometry feature
    id = "city_centroïds"
    tile_fields = ('name', 'city_code', 'area', 'population')  # add area and population properties in each tile feature
    min_zoom = 7  # let's show city name at zoom 7


    
# in your view file

from yourapp.vector_layers import CityVectorLayer, CityCentroidVectorLayer

from vectortiles.views import MVTView


class CityTileView(MVTView):
    layer_classes = [CityVectorLayer, CityCentroidVectorLayer]


# in your urls file
from django.urls import path
from yourapp import views

urlpatterns = [
    ...
    views.CityTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>
    ...
]
```

#### Use TileJSON and multiple domains:

```python
# in your view file

from django.urls import reverse

from vectortiles.views import MVTView, TileJSONView
from yourapp.vector_layers import CityVectorLayer, CityCentroidVectorLayer


class CityTileBaseView:
    layer_classes = [CityVectorLayer, CityCentroidVectorLayer]
    

class CityTileView(CityTileBaseView, MVTView):
    pass


class CityTileJSONView(CityTileBaseView, TileJSONView):
    """Simple model TileJSON View"""

    name = "My city dataset"
    attribution = "@JEC Data"
    description = "My vity dataset"


# in your urls file
from django.urls import path
from yourapp import views

urlpatterns = [
    ...
    CityTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>
    CityTileJSONView.get_url(name="city-tilejson"),  # serve tilejson at /tiles.json
    ...
]

# if you want to use multiple domains, you can set the allowed hosts and vector tiles urls in your settings file
# in your settings file
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

```



Now, any tile requested at http://you_url/tiles/{z}/{x}/{y} that intersects a city will return a vector tile with two layers, `cities` with border geometries and `city_code` property, and `city_centroïds` with center geometry and `city_name` property.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>City map</title>
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
                'id': 'background',
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
                "id": "commune_border",
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
                "id": "city_centroïds",
                "type": "symbol",
                "source": "layers",
                "source-layer": "city_centroïds",
                "minzoom": 10,
                "maxzoom": 12,
                "layout": {
                    "symbol-placement": "point",
                    "symbol-spacing": 350,
                    "text-field": "{name}\n{population} hab.\n{area} m²",
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

        map.on('mouseenter', 'commune_nom', function (e) {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';
            console.log(e.features);
            var coordinates = e.features[0].geometry.coordinates.slice();
            var description = `${e.features[0].properties.nom} (${e.features[0].properties.population} hab.)`;

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

        map.on('mouseleave', 'city-centroid', function () {
            map.getCanvas().style.cursor = '';
            popup.remove();
        });
    }
);
</script>
</body>
</html>

```

#### Usage with Django Rest Framework

django-vectortiles can be used with DRF if `renderer_classes` of the view is overridden (see [DRF docs](https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers)). Simply use the right BaseMixin and action on viewsets, or directly a GET method in an APIView. See [documentation](https://django-vectortiles.readthedocs.io/en/latest/usage.html#django-rest-framework) for more details.

#### Development

##### With docker and docker-compose

Copy ```.env.dist``` to ```.env``` and fill ```SECRET_KEY``` and ```POSTGRES_PASSWORD```

```bash
docker-compose build
# docker-compose up
docker-compose run /code/venv/bin/python ./manage.py test
```

##### Local

* Install python and django requirements (python 3.8+, django 3.2+)
* Install geodjango requirements
* Have a postgresql / postgis 2.4+ enabled database
* Use a virtualenv

```bash
pip install .[dev] -U
```
