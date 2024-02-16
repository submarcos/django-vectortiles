DEVELOPMENT
===========

With docker and docker-compose
******************************

Copy ```.env.dist``` to ```.env``` and fill ```SECRET_KEY``` and ```POSTGRES_PASSWORD```

.. code-block:: bash

    docker-compose build
    # docker-compose up
    docker-compose run /code/venv/bin/python ./manage.py test


Local
*****

* Install python and django requirements (python 3.8+, django 3.2+)
* Install geodjango requirements
* Have a postgresql / postgis 2.4+ enabled database
* Use a virtualenv

.. code-block:: bash

    pip install .[dev] -U
