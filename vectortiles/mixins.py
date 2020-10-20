import mercantile
from django.http import HttpResponse


class BaseVectorTileMixin:
    vector_tile_content_type = "application/x-protobuf"
    vector_tile_queryset = None
    vector_tile_layer_name = None  # name for data layer in vector tile
    vector_tile_geom_name = "geom"  # geom field to consider in qs
    vector_tile_fields = None  # other fields to include from qs
    vector_tile_generation = None  # use mapbox if you installed [mapbox] subdependencies
    vector_tile_extent = 4096
    vector_tile_buffer = 256

    def get_bounds(self, x, y, z):
        bounds = mercantile.bounds(x, y, z)
        xmin, ymin = mercantile.xy(bounds.west, bounds.south)
        xmax, ymax = mercantile.xy(bounds.east, bounds.north)
        return xmin, ymin, xmax, ymax

    def get_vector_tile_queryset(self):
        return self.vector_tile_queryset if self.vector_tile_queryset else self.get_queryset()

    def get_vector_tile_layer_name(self):
        return self.vector_tile_layer_name

    def get_tile(self, x, y, z, extent=4096, buffer=256, clip_geom=True):
        """
        Get bytearray representing a MapBoxVectorTile
        :param x: longitude coordinate tile
        :param y: latitude coordinate tile
        :param z: zoom level
        :param extent: tile extent
        :param buffer: buffer extent
        :param clip_geom: clip geometries
        :param geom_field: Geometry field name in subquery
        :param include_fields: extra fields to include in Vector tile
        :return: mvt as bytearray
        """
        raise NotImplementedError()


class BaseVectorTileView:
    content_type = None

    def get(self, request, z, x, y):
        content = self.get_tile(x, y, z, extent=self.vector_tile_extent, buffer=self.vector_tile_buffer, clip_geom=True)
        status = 200 if content else 204
        return HttpResponse(content, content_type=self.content_type, status=status)
