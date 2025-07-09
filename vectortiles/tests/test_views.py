import mapbox_vector_tile
from django.test import TestCase
from django.urls import reverse

from test_vectortiles.test_app.models import Feature, Layer
from vectortiles.views import MVTView, TileJSONView


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
            self.client.get(reverse("feature", args=(0, 0, 0)))

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
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": "Feature",
                        },
                        {
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [[2048, 2048], [2059, 2059]],
                            },
                            "properties": {"name": "feat2"},
                            "id": 0,
                            "type": "Feature",
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
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [2048, 2048]},
                            "properties": {"name": "feat1"},
                            "id": 0,
                            "type": "Feature",
                        }
                    ],
                }
            },
        )

    def test_get_url_defined_prefix_in_attribute(self):
        class TestView(MVTView):
            prefix_url = "test"

        self.assertEqual(
            str(TestView.get_url()), "<URLPattern 'test/<int:z>/<int:x>/<int:y>'>"
        )

    def test_get_url_defined_prefix_in_param(self):
        class TestView(MVTView):
            pass

        self.assertEqual(
            str(TestView.get_url(prefix="toto")),
            "<URLPattern 'toto/<int:z>/<int:x>/<int:y>'>",
        )

    def test_get_url_default_prefix(self):
        class TestView(MVTView):
            pass

        self.assertEqual(
            str(TestView.get_url()), "<URLPattern 'testview/<int:z>/<int:x>/<int:y>'>"
        )


class VectorTileTileJSONTestCase(VectorTileBaseTest):
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
                "bounds": [-180, -85.05112877980659, 180, 85.0511287798066],
                "center": None,
                "fillzoom": None,
                "legend": None,
                "maxzoom": 30,
                "scheme": "xyz",
                "minzoom": 0,
                "name": "Feature tileset",
                "tilejson": "3.0.0",
                "tiles": ["http://testserver/features/tile/{z}/{x}/{y}"],
                "vector_layers": [],
                "version": "1.0.0",
            },
        )

    def test_tilejson_view_default(self):
        class TestView(TileJSONView):
            tile_url = "test"

        instance = TestView()
        self.assertEqual(instance.tile_url, instance.get_tile_url())
