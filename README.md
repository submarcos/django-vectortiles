![Tests](https://github.com/submarcos/django-vectortiles/workflows/Unit%20tests/badge.svg)
[![Coverage](https://codecov.io/gh/submarcos/django-vectortiles/branch/master/graph/badge.svg)](https://codecov.io/gh/submarcos/django-vectortiles)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.8-blue.svg)
![Django Version](https://img.shields.io/badge/django-%3E%3D%204.2-blue.svg)

# Generate MapBox VectorTiles from GeoDjango models
![image](https://github.com/user-attachments/assets/46d5b475-c5c1-48b2-959d-9689968fdfef)

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
        area=Area("geom"), # compute the city area
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
from yourapp import views

urlpatterns = [
    ...
    views.CityTileView.get_url(),  # serve tiles at default /tiles/<int:z>/<int:x>/<int:y>
    ...
]
```

Now, any tile requested at http://you_url/tiles/{z}/{x}/{y} that intersects a city will return a vector tile with two layers, `cities` with border geometries and `city_code` property, and `city_centroïds` with center geometry and `city_name` property.
![image](https://github.com/user-attachments/assets/d472639a-db4c-40aa-984a-c68a8e841283)

[Read full documentation](https://django-vectortiles.readthedocs.io/) for examples, as multiple layers, cache policy, mapblibre integration, etc.
