import mercantile


class BaseVectorLayerMixin:
    """
    Base Mixin to handle vector tile generation
    """

    model = None
    queryset = None
    queryset_limit = None  # if you want to limit feature number per tile

    id = ""  # id for data layer in vector tile
    description = ""
    min_zoom = 0
    max_zoom = 22
    geom_field = "geom"  # geom field to consider in qs
    layer_fields = None  # fields description
    tile_fields = None  # other fields to include from qs
    tile_extent = 4096  # define tile extent
    tile_buffer = (
        256  # buffer around tiles (intersected polygon display without borders)
    )
    clip_geom = True  # geometry clipped in tile

    def check_in_zoom_levels(self, z):
        return self.get_min_zoom() <= z <= self.get_max_zoom()

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description

    def get_min_zoom(self):
        return self.min_zoom

    def get_max_zoom(self):
        return self.max_zoom

    def get_layer_fields(self):
        return self.layer_fields or {}

    def get_tile_fields(self):
        return self.tile_fields or ()

    def get_tilejson_vector_layer(self):
        return {
            "id": self.get_id(),
            "description": self.get_description(),
            "fields": self.get_layer_fields(),
            "minzoom": self.get_min_zoom(),
            "maxzoom": self.get_max_zoom(),
        }

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

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return self.model.objects.all()

    def get_vector_tile_queryset(self, *args, **kwargs):
        """Get feature queryset in tile dynamically"""
        return self.get_queryset()

    def get_queryset_limit(self):
        """Get feature limit by tile dynamically"""
        return self.queryset_limit

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
