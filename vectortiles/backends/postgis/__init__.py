from django.contrib.gis.db.models.functions import Transform
from django.db import connection

from vectortiles.backends import BaseVectorLayerMixin
from vectortiles.backends.postgis.functions import AsMVTGeom, MakeEnvelope


class VectorLayer(BaseVectorLayerMixin):
    def get_tile(self, x, y, z):
        if not self.check_in_zoom_levels(z):
            return b""
        features = self.get_vector_tile_queryset(z, x, y)
        # get tile coordinates from x, y and z
        xmin, ymin, xmax, ymax = self.get_bounds(x, y, z)
        # keep features intersecting tile
        filters = {
            # GeoFuncMixin implicitly transforms to SRID of geom
            f"{self.geom_field}__intersects": MakeEnvelope(xmin, ymin, xmax, ymax, 3857)
        }
        features = features.filter(**filters)
        # annotate prepared geometry for MVT
        features = features.annotate(
            geom_prepared=AsMVTGeom(
                Transform(self.geom_field, 3857),
                MakeEnvelope(xmin, ymin, xmax, ymax, 3857),
                self.tile_extent,
                self.tile_buffer,
                self.clip_geom,
            )
        )
        fields = (
            self.get_tile_fields() + ("geom_prepared",)
            if self.get_tile_fields()
            else ("geom_prepared",)
        )
        # limit feature number if limit provided
        limit = self.get_queryset_limit()
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
                    self.get_id(),
                    self.tile_extent,
                    "geom_prepared",
                    *params,
                ],
            )
            row = cursor.fetchone()[0]
            return row.tobytes() if row else b""
