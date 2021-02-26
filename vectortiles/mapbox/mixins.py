import math

import mapbox_vector_tile
from django.contrib.gis.db.models.functions import Intersection, Transform
from django.contrib.gis.geos import Polygon

from vectortiles.mixins import BaseVectorTileMixin


class MapboxBaseVectorTile(BaseVectorTileMixin):
    vector_tile_generation = "mapbox"

    def pixel_length(self, zoom, size=512):
        radius = 6378137
        circum = 2 * math.pi * radius
        return circum / size / 2 ** int(zoom)

    def get_tile(self, x, y, z):
        # get tile coordinates from x, y and z
        west, south, east, north = self.get_bounds(x, y, z)
        features = self.get_vector_tile_queryset()

        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 3857

        filters = {
            f"{self.vector_tile_geom_name}__intersects": bbox
        }
        features = features.filter(**filters)
        # limit feature number if limit provided
        limit = self.get_vector_tile_queryset_limit()
        if limit:
            features = features[:limit]
        features = features.annotate(clipped=Intersection(Transform(self.vector_tile_geom_name, 3857),
                                                          bbox.buffer(self.vector_tile_buffer)))
        if features:
            tile = {
                "name": self.get_vector_tile_layer_name(),
                "features": [
                    {
                        "geometry": feature.clipped.wkb.tobytes(),
                        "properties": {
                            key: getattr(feature, key) for key in self.vector_tile_fields if
                            self.vector_tile_fields
                        }
                    }
                    for feature in features
                ],
            }
            return mapbox_vector_tile.encode(tile,
                                             quantize_bounds=(west, south, east, north),
                                             extents=self.vector_tile_extent)
