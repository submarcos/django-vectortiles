from django.contrib.gis.db.models.functions import Transform
from django.db import connection

from vectortiles.postgis.functions import MakeEnvelope, AsMVTGeom

from vectortiles.mixins import BaseVectorTileMixin


class PostgisBaseVectorTile(BaseVectorTileMixin):
    def get_tile(self, x, y, z):
        # get tile coordinates from x, y and z
        xmin, ymin, xmax, ymax = self.get_bounds(x, y, z)
        features = self.get_vector_tile_queryset()

        # keep features intersecting tile
        filters = {
            # GeoFuncMixin implicitly transforms to SRID of geom
            f"{self.vector_tile_geom_name}__intersects": MakeEnvelope(xmin, ymin, xmax, ymax, 3857)
        }
        features = features.filter(**filters)
        # annotate prepared geometry for MVT
        features = features.annotate(geom_prepared=AsMVTGeom(Transform(self.vector_tile_geom_name, 3857),
                                                             MakeEnvelope(xmin, ymin, xmax, ymax, 3857),
                                                             self.vector_tile_extent,
                                                             self.vector_tile_buffer,
                                                             self.vector_tile_clip_geom))
        # limit feature number if limit provided
        limit = self.get_vector_tile_queryset_limit()
        if limit:
            features = features[:limit]
        all_sql = []
        all_params = []
        for layer_features, layer_name, extra_fields in self.iter_layer_features(features):
            fields = (extra_fields or ()) + ("geom_prepared",)
            # keep values to include in tile (extra included_fields + geometry)
            layer_features = layer_features.values(*fields)
            # generate MVT
            sql, params = layer_features.query.sql_with_params()
            all_sql.append(sql)
            all_params.append([
                layer_name,
                self.vector_tile_extent,
                'geom_prepared',
                *params,
            ])
        with connection.cursor() as cursor:
            sql = ', '.join(
                "(SELECT ST_ASMVT({}.*, %s, %s, %s) FROM ({}) as {}) AS {}".format(f'q{ii}', sql, f'q{ii}', f'w{ii}')
                for ii, sql in enumerate(all_sql)
            )
            params = sum(all_params, [])
            cursor.execute(f"SELECT {sql}", params=params)
            return b''.join((r.tobytes() if r else b'') for r in cursor.fetchone())
