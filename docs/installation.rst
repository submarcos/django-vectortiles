INSTALLATION
============

Requirements
************

* You need to install geodjango required libraries (See `here <https://docs.djangoproject.com/en/3.1/ref/contrib/gis/install/geolibs/>`_)

PostGIS 2.4+ backend usage
**************************

* You need a PostgreSQL database with PostGIS 2.4+ extension enabled. (See `<https://docs.djangoproject.com/en/3.1/ref/contrib/gis/install/postgis/>`_)

* You need to enable and use **django.contrib.gis.db.backends.postgis** database backend

.. code-block:: bash

   pip install psycopg2
   pip install django-vectortiles


Other database backend usages
*****************************

.. code-block:: bash

   pip install django-vectortiles[mapbox]

This will include sub-dependencies to generate vector tiles from mapbox_vector_tiles python library.
