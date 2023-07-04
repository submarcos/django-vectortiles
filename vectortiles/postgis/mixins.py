from django.contrib.gis.db.models.functions import Transform
from django.db import connection

from vectortiles.mixins import BaseVectorTileMixin
from vectortiles.postgis.functions import AsMVTGeom, MakeEnvelope


class PostgisBaseVectorTile(BaseVectorTileMixin):
    def get_tile(self, x, y, z):
        # get tile coordinates from x, y and z
        xmin, ymin, xmax, ymax = self.get_bounds(x, y, z)
        features = self.get_vector_tile_queryset()

        # keep features intersecting tile
        filters = {
            # GeoFuncMixin implicitly transforms to SRID of geom
            f"{self.vector_tile_geom_name}__intersects": MakeEnvelope(
                xmin, ymin, xmax, ymax, 3857
            )
        }
        features = features.filter(**filters)
        # annotate prepared geometry for MVT
        features = features.annotate(
            geom_prepared=AsMVTGeom(
                Transform(self.vector_tile_geom_name, 3857),
                MakeEnvelope(xmin, ymin, xmax, ymax, 3857),
                self.vector_tile_extent,
                self.vector_tile_buffer,
                self.vector_tile_clip_geom,
            )
        )
        fields = (
            self.vector_tile_fields + ("geom_prepared",)
            if self.vector_tile_fields
            else ("geom_prepared",)
        )
        # limit feature number if limit provided
        limit = self.get_vector_tile_queryset_limit()
        if limit:
            features = features[:limit]
        # keep values to include in tile (extra included_fields + geometry)
        features = features.values(*fields)
        # generate MVT
        sql, params = features.query.sql_with_params()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ST_ASMVT(subquery.*, %s, %s, %s) FROM ({}) as subquery".format(
                    sql
                ),
                params=[
                    self.get_vector_tile_layer_name(),
                    self.vector_tile_extent,
                    "geom_prepared",
                    *params,
                ],
            )
            row = cursor.fetchone()[0]
            if row:
                return row.tobytes() if type(row) == memoryview else row
            return b""

