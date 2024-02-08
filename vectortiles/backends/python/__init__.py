import math

import mapbox_vector_tile
from django.contrib.gis.db.models.functions import Intersection, Transform
from django.contrib.gis.geos import Polygon
from django.db.models import F

from vectortiles.backends import BaseVectorLayerMixin


class VectorLayer(BaseVectorLayerMixin):
    def pixel_length(self, zoom, size):
        radius = 6378137
        circum = 2 * math.pi * radius
        return circum / size / 2 ** int(zoom)

    def get_tile(self, x, y, z):
        if not self.check_in_zoom_levels(z):
            return b""

        features = self.get_vector_tile_queryset(z, x, y)

        # get tile coordinates from x, y and z
        west, south, east, north = self.get_bounds(x, y, z)
        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 3857

        filters = {f"{self.geom_field}__intersects": bbox}
        features = features.filter(**filters)
        # limit feature number if limit provided
        limit = self.get_queryset_limit()
        if limit:
            features = features[:limit]
        features = features.annotate(
            clipped=Intersection(
                Transform(self.geom_field, 3857),
                bbox.buffer(self.pixel_length(z, self.tile_buffer)),
            )
            if self.clip_geom
            else F("geom")
        )
        if features:
            tile = {
                "name": self.get_id(),
                "features": [
                    {
                        "geometry": feature.clipped.wkb.tobytes(),
                        "properties": {
                            key: getattr(feature, key)
                            for key in self.tile_fields
                            if self.tile_fields
                        },
                    }
                    for feature in features
                ],
            }
            return mapbox_vector_tile.encode(
                tile,
                quantize_bounds=(west, south, east, north),
                extents=self.tile_extent,
            )
