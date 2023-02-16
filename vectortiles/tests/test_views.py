import mapbox_vector_tile
from django.test import TestCase
from django.urls import reverse

from test_vectortiles.test_app.models import Feature, Layer
from vectortiles.views import TileJSONView


class VectorTileBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.layer = Layer.objects.create(name="features")
        Feature.objects.create(
            name="feat1", geom="POINT(0 0)", layer=cls.layer, date="2020-07-07"
        )
        Feature.objects.create(
            name="feat2",
            geom="LINESTRING(0 0, 1 1)",
            layer=cls.layer,
            date="2020-08-08",
        )


class VectorTileTestCase(VectorTileBaseTest):
    def test_num_queries_equals_one(self):
        self.maxDiff = None
        with self.assertNumQueries(1):
            self.client.get(
                reverse("feature-with-manual-vector-tile-queryset", args=(0, 0, 0))
            )

    def test_layer(self):
        self.maxDiff = None
        response = self.client.get(reverse("layer", args=(self.layer.pk, 0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 1,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": 2,
                        },
                    ],
                }
            },
            content,
        )

    def test_features(self):
        self.maxDiff = None
        response = self.client.get(reverse("feature", args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 2,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": 2,
                        },
                    ],
                }
            },
        )

    def test_layer(self):
        self.maxDiff = None
        response = self.client.get(reverse("layer", args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 2,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": 2,
                        },
                    ],
                }
            },
        )

    def test_drf_api_features(self):
        self.maxDiff = None
        response = self.client.get(reverse("feature-drf", args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 2,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": 2,
                        },
                    ],
                }
            },
        )

    def test_drf_viewset_features(self):
        self.maxDiff = None
        response = self.client.get(reverse("feature-drf-viewset-tile", args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 2,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": 2,
                        },
                    ],
                }
            },
        )

    def test_features_with_filtered_date(self):
        self.maxDiff = None
        response = self.client.get(reverse("feature-date", args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {
                "features": {
                    "extent": 4096,
                    "version": 2,
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": 1,
                        }
                    ],
                }
            },
        )


class VectorTileTileJSONTestCase(VectorTileBaseTest):
    def test_layer(self):
        self.maxDiff = None
        response = self.client.get(reverse("layer-tilejson", args=(self.layer.pk,)))
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertDictEqual(
            content,
            {
                "attribution": "© JEC",
                "description": "generated from data",
                "maxzoom": 22,
                "minzoom": 0,
                "name": "Layer's features tileset",
                "tilejson": "3.0.0",
                "tiles": ["/layer/2/tile/{z}/{x}/{y}"],
                "vector_layers": [
                    {
                        "description": "Feature layer",
                        "fields": {},
                        "id": "features",
                        "maxzoom": 22,
                        "minzoom": 0,
                    }
                ],
            },
        )

    def test_features(self):
        self.maxDiff = None
        response = self.client.get(reverse("feature-tilejson"))
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertDictEqual(
            content,
            {
                "attribution": "© JEC",
                "description": "feature tileset",
                "maxzoom": 22,
                "minzoom": 0,
                "name": "Feature tileset",
                "tilejson": "3.0.0",
                "tiles": ["/features/tile/{z}/{x}/{y}"],
                "vector_layers": [
                    {
                        "description": "Feature layer",
                        "fields": {},
                        "id": "features",
                        "maxzoom": 22,
                        "minzoom": 0,
                    }
                ],
            },
        )

    def test_tilejson_view_default(self):
        class TestView(TileJSONView):
            tile_url = "test"

        instance = TestView()
        self.assertEqual(instance.tile_url, instance.get_tile_url())
