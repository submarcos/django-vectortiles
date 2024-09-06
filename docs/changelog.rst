=========
Changelog
=========

1.0.0    (2024-09-04)
---------------------

**Breaking changes**

  * Refactor PostGIS and Python (old named MapBox) backends usage. Use setting to set (default postgis)
  * No DetailView anymore. As Tile can have many layers, declare VectorLayer on MVTView (one or many).

**Enhancements**

  * Add compatibility to use with psycopg v3
  * Drop python 3.6 and Django 2.2, 3.2
  * Add python 3.11, 3.12 and Django 4.2, 5.0, 5.1

* Features

  * Native MVTRenderer for django-rest-framework

* Quality

  * Black-ified
  * iSort-ed

* Documentation

  * Add DRF and MapLibre examples


0.2.0       (2022-10-17)
------------------------

* Possibly breaking change:
  * Base Mixin method get_tile use now class attributes for extent / buffer or clip_geom. Remove this parameters in your sub class method if needed.

* Bug fixes:
  * Correct usage for vector_tile_extent / vector_tile_buffer and vector_tile_clip_geom
  * Clipped geom is now working for mapbox

* Support Python 3.10 and django 4.1
  

0.1.0       (2021-02-25)
------------------------

First beta release

* Add attribute to limit features in tile (unable to use a sliced queryset)


0.0.3       (2021-02-18)
------------------------

* Delete useless Envelope transformation because django implicitly transform on intersects lookup (thanks to StefanBrand)
* Avoid useless queryset evaluation in some cases (thanks to StefanBrand)


0.0.2       (2021-02-12)
------------------------

* Fix required 'fields' key in tilejson. Will be filled later
* Fix generated subquery to deal with DateField (thanks to StefanBrand)


0.0.1       (2020-10-22)
------------------------

# First Release

  * Generate Vector Tiles from django models
      * in python
      * with PostGIS
  * Generate associated TileJSON
  * Default views to handle Vector tiles and tilejson
 
