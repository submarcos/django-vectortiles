from urllib.parse import unquote, urljoin

from vectortiles import settings as app_settings


class BaseVectorView:
    layers = None

    def get_layers(self):
        return self.layers or []


class BaseTileJSONView(BaseVectorView):
    # https://github.com/mapbox/tilejson-spec/tree/master/3.0.0
    name = None
    attribution = None
    description = None
    min_zoom = None  # 0 - 30 range. lower than equal than max_zoom. By default, it's min_zoom of all layers.
    max_zoom = None  # 0 - 30 range. greater than equal than min_zoom. By default, it's max_zoom of all layers.
    fill_zoom = None
    legend = None
    bounds = [-180, -85.05112877980659, 180, 85.0511287798066]
    center = None
    scheme = "xyz"
    version = "1.0.0"

    def __init__(self, *args, **kwargs):
        if self.get_min_zoom() > self.get_max_zoom():
            raise ValueError("min_zoom must be lower than equal than max_zoom")
        if self.get_max_zoom() < self.get_min_zoom():
            raise ValueError("max_zoom must be greater than equal than min_zoom")
        if not (0 <= self.get_min_zoom() <= 30):
            raise ValueError("min_zoom should be in range 0 - 30")
        if not (0 <= self.get_max_zoom() <= 30):
            raise ValueError("max_zoom should be in range 0 - 30")
        super().__init__(*args, **kwargs)

    def get_min_zoom(self):
        """Get tilejson minzoom from layers or self.min_zoom"""
        try:
            # minimum zoom level from layers
            layers_min_zoom = min(layer.get_min_zoom() for layer in self.get_layers())
        except ValueError:
            # case there is no layer defined ...
            layers_min_zoom = None

        if self.min_zoom is not None:
            # if defined, return max of layers_min_zoom and self.min_zoom
            return (
                max(layers_min_zoom, self.min_zoom)
                if layers_min_zoom is not None
                else self.min_zoom
            )
        # if self.min_zoom not defined, return layers_min_zoom or 0
        return layers_min_zoom if layers_min_zoom is not None else 0

    def get_max_zoom(self):
        """Get tilejson manzoom from layers or self.man_zoom"""
        try:
            # maximum zoom level from layers
            layers_max_zoom = min(layer.get_max_zoom() for layer in self.get_layers())
        except ValueError:
            # case there is no layer defined ...
            layers_max_zoom = None

        if self.max_zoom is not None:
            # if defined, return min of layers_max_zoom and self.max_zoom
            return (
                min(layers_max_zoom, self.max_zoom)
                if layers_max_zoom is not None
                else self.max_zoom
            )
        # if self.max_zoom not defined, return layers_max_zoom or 30
        return layers_max_zoom if layers_max_zoom is not None else 30

    def get_fill_zoom(self):
        return self.fill_zoom

    def get_attribution(self):
        return self.attribution

    def get_legend(self):
        return self.legend

    def get_description(self):
        return self.description

    def get_name(self):
        return self.name

    def get_bounds(self):
        return self.bounds

    def get_center(self):
        return self.center

    def get_scheme(self):
        return self.scheme

    def get_version(self):
        return self.version

    def get_tile_urls(self, tile_url):
        if app_settings.VECTOR_TILES_URLS:
            return [
                unquote(urljoin(hostname, tile_url))
                for hostname in app_settings.VECTOR_TILES_URLS
            ]
        else:
            return [unquote(self.request.build_absolute_uri(tile_url))]

    def get_tilejson(self, tile_url, version="3.0.0"):
        # https://github.com/mapbox/tilejson-spec/tree/master/3.0.0
        return {
            "tilejson": version,
            "name": self.get_name(),
            "description": self.get_description(),
            "legend": self.get_legend(),
            "attribution": self.get_attribution(),
            "tiles": self.get_tile_urls(tile_url),
            "minzoom": self.get_min_zoom(),
            "maxzoom": self.get_max_zoom(),
            "fillzoom": self.get_fill_zoom(),
            "bounds": self.get_bounds(),
            "center": self.get_center(),
            "scheme": self.get_scheme(),
            "version": self.get_version(),
            "vector_layers": [
                layer.get_tilejson_vector_layer() for layer in self.get_layers()
            ],
        }


class BaseVectorTileView(BaseVectorView):
    """Base mixin to handle vector tile in a django View"""

    content_type = app_settings.VECTOR_TILES_CONTENT_TYPE

    def get_layer_tiles(self, z, x, y):
        layers = self.get_layers()
        if layers:
            return b"".join(layer.get_tile(x, y, z) for layer in layers)
        raise Exception("No layers defined")

    def get_content_status(self, z, x, y):
        content = self.get_layer_tiles(z, x, y)
        return (content, 200) if content else (content, 204)
