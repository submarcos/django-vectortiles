import mapbox_vector_tile
from django.test import TestCase
from django.urls import reverse

from test_vectortiles.test_app.models import Layer, Feature


class VectorTileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.layer = Layer.objects.create(
            name="features"
        )
        Feature.objects.create(
            name="feat1",
            geom="POINT(0 0)",
            layer=cls.layer
        )
        Feature.objects.create(
            name="feat2",
            geom="LINESTRING(0 0, 1 1)",
            layer=cls.layer
        )

    def test_mapbox_layer(self):
        self.maxDiff = None
        response = self.client.get(reverse('layer-mapbox', args=(self.layer.pk, 0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {'features': {
                'extent': 4096,
                'version': 1,
                'features': [{'geometry': {'type': 'Point', 'coordinates': [2048, 2048]},
                              'properties': {'name': 'feat1'}, 'id': 0, 'type': 1},
                             {'geometry': {'type': 'LineString', 'coordinates': [[2048, 2048], [2059, 2059]]},
                              'properties': {'name': 'feat2'}, 'id': 0, 'type': 2}]
            }},
            content
        )

    def test_mapbox_features(self):
        self.maxDiff = None
        response = self.client.get(reverse('feature-mapbox', args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {'features': {
                'extent': 4096,
                'version': 1,
                'features': [{'geometry': {'type': 'Point', 'coordinates': [2048, 2048]},
                              'properties': {'name': 'feat1'}, 'id': 0, 'type': 1},
                             {'geometry': {'type': 'LineString', 'coordinates': [[2048, 2048], [2059, 2059]]},
                              'properties': {'name': 'feat2'}, 'id': 0, 'type': 2}]
            }})

    def test_postgis_layer(self):
        self.maxDiff = None
        response = self.client.get(reverse('layer-postgis', args=(self.layer.pk, 0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {'features': {
                'extent': 4096,
                'version': 2,
                'features': [{'geometry': {'type': 'Point', 'coordinates': [2048, 2048]},
                              'properties': {'name': 'feat1'}, 'id': 0, 'type': 1},
                             {'geometry': {'type': 'LineString', 'coordinates': [[2048, 2048], [2059, 2059]]},
                              'properties': {'name': 'feat2'}, 'id': 0, 'type': 2}]
            }})

    def test_postgis_features(self):
        self.maxDiff = None
        response = self.client.get(reverse('feature-postgis', args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        content = mapbox_vector_tile.decode(response.content)
        self.assertDictEqual(
            content,
            {'features': {
                'extent': 4096,
                'version': 2,
                'features': [{'geometry': {'type': 'Point', 'coordinates': [2048, 2048]},
                              'properties': {'name': 'feat1'}, 'id': 0, 'type': 1},
                             {'geometry': {'type': 'LineString', 'coordinates': [[2048, 2048], [2059, 2059]]},
                              'properties': {'name': 'feat2'}, 'id': 0, 'type': 2}]
            }})
