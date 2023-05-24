#!/usr/bin/env python

import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(HERE, 'README.md')).read()

test_require = [
    'factory-boy',
    'flake8',
    'isort',
    'black',
    'coverage',
    'djangorestframework',
    'psycopg2-binary'  # for dev and test only. in production, use psycopg2
]

python = [
    'mapbox_vector_tile',
    'protobuf<4.21.0',  # https://github.com/tilezen/mapbox-vector-tile/issues/113
]

setup(
    name='django-vectortiles',
    version=open(os.path.join(HERE, 'vectortiles', 'VERSION.md')).read().strip(),
    include_package_data=True,
    author="Jean-Etienne Castagnede",
    description='Django vector tile generation',
    long_description=README,
    description_content_type="text/markdown",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url='https://github.com/submarcos/django-vectortiles.git',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.6',
    install_requires=[
        'django',
        'mercantile'
    ],
    tests_require=test_require,
    extras_require={
        'test': test_require,
        'dev': test_require + python + [
            'django-debug-toolbar', 'sphinx-rtd-theme'
        ],
        'python': python,
        'mapbox': python
    }
)
