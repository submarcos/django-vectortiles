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
* Ensure you have psycopg2 set and installed

#### If you don't want to use Postgis and / or PostgreSQL
```bash
pip install django-vectortiles[python]
```
* This will incude mapbox_vector_tiles package and its dependencies
* Set VECTOR_TILES_BACKEND to "vectortiles.backends.python"

### Examples

* assuming you have django.contrib.gis in your INSTALLED_APPS and a gis compatible database backend

```python
# in your app models.py

from django.contrib.gis.db import models


class Feature(models.Model):
    geom = models.GeometryField(srid=4326)
    name = models.CharField(max_length=250)
```


#### Simple Example:

```python
# in a vector_layers.py file
from vectortiles import VectorLayer
from yourapp.models import Feature


class FeatureVectorLayer(VectorLayer):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ("name",)

# in your view file

from vectortiles.views import MVTView
from yourapp.vector_layers import FeatureVectorLayer


class FeatureTileView(MVTView):
    layers = [FeatureVectorLayer()]


# in your urls file
from django.urls import path
from yourapp import views


urlpatterns = [
    ...
    path('tiles/<int:z>/<int:x>/<int:y>', views.FeatureTileView.as_view(), name="feature-tile"),
    ...
]
```

#### Related model:

```python
# in your view file

from django.views.generic import DetailView
from vectortiles.mixins import BaseVectorTileView
from vectortiles.postgis.views import MVTView
from yourapp.models import Layer


class LayerTileView(MVTView, DetailView):
    model = Layer
    vector_tile_fields = ('other_field_to_include', )

    def get_vector_tile_layer_name(self):
        return self.get_object().name

    def get_vector_tile_queryset(self):
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
```

#### Usage without PostgreSQL / PostGIS

Just import and use vectortiles.mapbox.view.MVTView instead of vectortiles.postgis.view.MVTView

#### Usage with Django Rest Framework

django-vectortiles can be used with DRF if `renderer_classes` of the view is overridden (see [DRF docs](https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers)). Simply use the right BaseMixin and action on viewsets, or directly a GET method in an APIView. See [documentation](https://django-vectortiles.readthedocs.io/en/latest/usage.html#django-rest-framework) for more details.

#### Development

##### With docker and docker-compose

```bash
docker-compose build
# docker-compose up
docker-compose run /code/venv/bin/python ./manage.py test
```

##### Local

* Install python and django requirements (python 3.6+, django 2.2+)
* Install geodjango requirements
* Have a postgresql / postgis 2.4+ enabled database
* Use a virtualenv
```bash
pip install .[dev] -U
```
