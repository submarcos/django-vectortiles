from urllib.parse import unquote, urljoin

from vectortiles import settings as app_settings


class BaseVectorView:
    layers = None

    def get_layers(self):
        return self.layers or []


class BaseTileJSONView(BaseVectorView):
    vector_tile_tilejson_name = ""
    vector_tile_tilejson_attribution = ""
    vector_tile_tilejson_description = ""

    def get_vector_tile_tilejson_min_zoom(self):
        min_zoom = min(
            layer.get_tilejson_vector_layer()["minzoom"] for layer in self.get_layers()
        )
        return min_zoom or 0

    def get_vector_tile_tilejson_max_zoom(self):
        max_zoom = max(
            layer.get_tilejson_vector_layer()["maxzoom"] for layer in self.get_layers()
        )
        return max_zoom or 22

    def get_vector_tile_tilejson_attribution(self):
        return self.vector_tile_tilejson_attribution

    def get_vector_tile_tilejson_description(self):
        return self.vector_tile_tilejson_description

    def get_vector_tile_tilejson_name(self):
        return self.vector_tile_tilejson_name

    def get_tile_urls(self, tile_url):
        if app_settings.VECTOR_TILES_HOSTNAMES:
            return [
                unquote(urljoin(hostname, tile_url))
                for hostname in app_settings.VECTOR_TILES_HOSTNAMES
            ]
        else:
            return [unquote(self.request.build_absolute_uri(tile_url))]

    def get_tilejson(self, tile_url, version="3.0.0"):
        # https://github.com/mapbox/tilejson-spec/tree/3.0/3.0.0
        return {
            "tilejson": version,
            "name": self.get_vector_tile_tilejson_name(),
            "tiles": self.get_tile_urls(tile_url),
            "minzoom": self.get_vector_tile_tilejson_min_zoom(),
            "maxzoom": self.get_vector_tile_tilejson_max_zoom(),
            # bounds
            # center
            "attribution": self.get_vector_tile_tilejson_attribution(),
            "description": self.get_vector_tile_tilejson_description(),
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
