CHANGELOG
=========


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

* First Release
  * Generate Vector Tiles from django models
      * in python
      * with PostGIS
  * Generate associated TileJSON
  * Default views to handle Vector tiles and tilejson
 
