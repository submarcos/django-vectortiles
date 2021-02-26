from urllib.parse import unquote

import mercantile
from django.http import HttpResponse


class BaseVectorTileMixin:
    """
    Base Mixin to handle vector tile generation
    """
    vector_tile_content_type = "application/x-protobuf"
    vector_tile_queryset = None
    vector_tile_queryset_limit = None
    vector_tile_layer_name = None  # name for data layer in vector tile
    vector_tile_geom_name = "geom"  # geom field to consider in qs
    vector_tile_fields = None  # other fields to include from qs
    vector_tile_generation = None  # use mapbox if you installed [mapbox] subdependencies
    vector_tile_extent = 4096  # define tile extent
    vector_tile_buffer = 256  # define buffer around tiles (intersected polygon display without borders)
    vector_tile_clip_geom = True  # define if feature geometries should be clipped in tile

    @classmethod
    def get_bounds(cls, x, y, z):
        """
        Get extent from xyz tile extent to 3857

        :param x: longitude coordinate tile
        :type x: int
        :param y: latitude coordinate tile
        :type y: int
        :param z: zoom level
        :type z: int

        :return: xmin, ymin, xmax, ymax in 3857 coordinate system
        :rtype: tuple
        """
        return mercantile.xy_bounds(x, y, z)

    def get_vector_tile_queryset(self):
        """ Get feature queryset in tile dynamically """
        return self.vector_tile_queryset if self.vector_tile_queryset is not None else self.get_queryset()

    def get_vector_tile_queryset_limit(self):
        """ Get feature limit by tile dynamically """
        return self.vector_tile_queryset_limit

    def get_vector_tile_layer_name(self):
        """ Get layer name in tile dynamically """
        return self.vector_tile_layer_name

    def get_tile(self, x, y, z):
        """
        Generate a mapbox vector tile as bytearray

        :param x: longitude coordinate tile
        :type x: int
        :param y: latitude coordinate tile
        :type y: int
        :param z: zoom level
        :type z: int

        :return: Mapbox Vector Tile
        :rtype: bytearray
        """
        raise NotImplementedError()


class VectorLayer:
    vector_tile_layer_id = ""
    vector_tile_layer_description = ""
    vector_tile_layer_min_zoom = 0
    vector_tile_layer_max_zoom = 22

    def __init__(self, id_layer, description="", min_zoom=0, max_zoom=22):
        self.vector_tile_layer_id = id_layer
        self.vector_tile_layer_description = description
        self.vector_tile_layer_min_zoom = min_zoom
        self.vector_tile_layer_max_zoom = max_zoom

    def get_vector_tile_layer_id(self):
        return self.vector_tile_layer_id

    def get_vector_tile_layer_description(self):
        return self.vector_tile_layer_description

    def get_vector_tile_layer_min_zoom(self):
        return self.vector_tile_layer_min_zoom

    def get_vector_tile_layer_max_zoom(self):
        return self.vector_tile_layer_max_zoom

    def get_vector_layer(self):
        return {
            'id': self.get_vector_tile_layer_id(),
            'description': self.get_vector_tile_layer_description(),
            'fields': {},  # self.layer_fields(layer),
            'minzoom': self.get_vector_tile_layer_min_zoom(),
            'maxzoom': self.get_vector_tile_layer_max_zoom(),
        }


class BaseTileJSONMixin:
    vector_tile_tilejson_name = ""
    vector_tile_tilejson_attribution = ""
    vector_tile_tilejson_description = ""

    def get_vector_tile_tilejson_min_zoom(self):
        min_zoom = min(item['minzoom'] for item in self.get_vector_layers())
        return min_zoom or 0

    def get_vector_tile_tilejson_max_zoom(self):
        max_zoom = max(item['maxzoom'] for item in self.get_vector_layers())
        return max_zoom or 22

    def get_vector_tile_tilejson_attribution(self):
        return self.vector_tile_tilejson_attribution

    def get_vector_tile_tilejson_description(self):
        return self.vector_tile_tilejson_description

    def get_vector_tile_tilejson_name(self):
        return self.vector_tile_tilejson_name

    def get_tile_urls(self, tile_url, base_url=''):
        # if app_settings.TERRA_TILES_HOSTNAMES:
        #     return [
        #         unquote(urljoin(hostname, tile_url))
        #         for hostname in app_settings.VECTOR_TILES_HOSTNAMES
        #     ]
        # else:
        return [
            unquote(tile_url)
        ]

    def get_vector_layers(self):
        raise NotImplementedError(""" you should implement get_vector_layers to return a VectorLayer list """)

    def get_tilejson(self, tile_url, version="3.0.0"):
        # https://github.com/mapbox/tilejson-spec/tree/3.0/3.0.0
        return {
            'tilejson': version,
            'name': self.get_vector_tile_tilejson_name(),
            'tiles': self.get_tile_urls(tile_url),
            'minzoom': self.get_vector_tile_tilejson_min_zoom(),
            'maxzoom': self.get_vector_tile_tilejson_max_zoom(),
            # bounds
            # center
            'attribution': self.get_vector_tile_tilejson_attribution(),
            'description': self.get_vector_tile_tilejson_description(),
            'vector_layers': self.get_vector_layers(),
        }


class BaseVectorTileView:
    """ Base mixin to handle vector tile in a djang oView """
    content_type = "application/vnd.mapbox-vector-tile"

    def get(self, request, z, x, y):
        """
        Handle GET request to serve tile

        :param request:
        :type request: HttpRequest
        :param x: longitude coordinate tile
        :type x: int
        :param y: latitude coordinate tile
        :type y: int
        :param z: zoom level
        :type z: int

        :rtype HTTPResponse
        """
        content = self.get_tile(x, y, z)
        status = 200 if content else 204
        return HttpResponse(content, content_type=self.content_type, status=status)
