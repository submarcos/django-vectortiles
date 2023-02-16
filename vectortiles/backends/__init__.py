import mercantile


class BaseVectorLayerMixin:
    """
    Base Mixin to handle vector tile generation
    """

    model = None
    queryset = None

    vector_tile_queryset = None
    vector_tile_queryset_limit = None  # if you want to limit element in tile
    vector_tile_layer_name = None  # name for data layer in vector tile
    vector_tile_geom_name = "geom"  # geom field to consider in qs
    vector_tile_fields = None  # other fields to include from qs
    vector_tile_generation = (
        None  # use mapbox if you installed [mapbox] sub-dependencies
    )
    vector_tile_extent = 4096  # define tile extent
    vector_tile_buffer = (
        256  # define buffer around tiles (intersected polygon display without borders)
    )
    vector_tile_clip_geom = (
        True  # define if feature geometries should be clipped in tile
    )
    vector_tile_layer_id = ""
    vector_tile_layer_description = ""
    vector_tile_layer_min_zoom = 0
    vector_tile_layer_max_zoom = 22

    def check_in_zoom_levels(self, z):
        return self.get_vector_tile_layer_min_zoom() <= z <= self.get_vector_tile_layer_max_zoom()

    def get_vector_tile_layer_id(self):
        return self.vector_tile_layer_id

    def get_vector_tile_layer_description(self):
        return self.vector_tile_layer_description

    def get_vector_tile_layer_min_zoom(self):
        return self.vector_tile_layer_min_zoom

    def get_vector_tile_layer_max_zoom(self):
        return self.vector_tile_layer_max_zoom

    def get_tilejson_vector_layer(self):
        return {
            "id": self.get_vector_tile_layer_id(),
            "description": self.get_vector_tile_layer_description(),
            "fields": {},  # self.layer_fields(layer),
            "minzoom": self.get_vector_tile_layer_min_zoom(),
            "maxzoom": self.get_vector_tile_layer_max_zoom(),
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
        return (
            self.vector_tile_queryset
            if self.vector_tile_queryset is not None
            else self.get_queryset()
        )

    def get_vector_tile_queryset_limit(self):
        """Get feature limit by tile dynamically"""
        return self.vector_tile_queryset_limit

    def get_vector_tile_layer_name(self):
        """Get layer name in tile dynamically"""
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
