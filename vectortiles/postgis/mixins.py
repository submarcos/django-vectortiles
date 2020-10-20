from django.contrib.gis.db.models.functions import Transform
from django.db import connection

from vectortiles.postgis.functions import MakeEnvelope, AsMVTGeom

from vectortiles.mixins import BaseVectorTileMixin


class PostgisBaseVectorTile(BaseVectorTileMixin):
    def get_tile(self, x, y, z, extent=4096, buffer=256, clip_geom=True):
        # get tile coordinates from x, y and z
        xmin, ymin, xmax, ymax = self.get_bounds(x, y, z)
        features = self.get_vector_tile_queryset()

        # keep features intersecting tile
        filters = {
            f"{self.vector_tile_geom_name}__intersects": Transform(MakeEnvelope(xmin, ymin, xmax, ymax, 3857),
                                                                   4326)
        }
        features = features.filter(**filters)
        # annotate prepared geometry for MVT
        features = features.annotate(geom_prepared=AsMVTGeom(self.vector_tile_geom_name,
                                                             MakeEnvelope(xmin, ymin, xmax, ymax, 3857),
                                                             extent,
                                                             buffer,
                                                             clip_geom))
        fields = self.vector_tile_fields + ("geom_prepared", ) if self.vector_tile_fields else ("geom_prepared", )
        # keep values to include in tile (extra included_fields + geometry)
        features = features.values(*fields)
        # generate MVT
        with connection.cursor() as cursor:
            cursor.execute("SELECT ST_ASMVT(subquery.*, %s, %s, %s) FROM ({}) as subquery".format(features.query),
                           params=[self.get_vector_tile_layer_name(), extent, "geom_prepared"])
            row = cursor.fetchone()[0]
            return row.tobytes() if row else None
