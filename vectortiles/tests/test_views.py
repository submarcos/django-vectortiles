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
            geom="POINT(1 1)",
            layer=cls.layer
        )

    def test_mapbox_layer(self):
        self.maxDiff = None
        expected_content = b'\x1aE\n\x08features\x12\r\x12\x02\x00\x00\x18\x01"\x05\t\x80 \x80 \x12\r\x12\x02\x00\x01'\
                           b'\x18\x01"\x05\t\x80 \x80 \x1a\x04name"\x07\n\x05feat2"\x07\n\x05feat1(\x80 x\x01'
        response = self.client.get(reverse('layer-mapbox', args=(self.layer.pk, 0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_content, response.content)

    def test_mapbox_features(self):
        self.maxDiff = None
        expected_content = b'\x1aE\n\x08features\x12\r\x12\x02\x00\x00\x18\x01"\x05\t\x80 \x80 \x12\r\x12\x02\x00\x01' \
                           b'\x18\x01"\x05\t\x80 \x80 \x1a\x04name"\x07\n\x05feat1"\x07\n\x05feat2(\x80 x\x01'
        response = self.client.get(reverse('feature-mapbox', args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_content, response.content)

    def test_postgis_layer(self):
        self.maxDiff = None
        expected_content = b'\x1aE\n\x08features\x12\r\x12\x02\x00\x00\x18\x01"\x05\t\x80 \x80 \x12\r\x12\x02\x00\x01' \
                           b'\x18\x01"\x05\t\x80 \x80 \x1a\x04name"\x07\n\x05feat2"\x07\n\x05feat1(\x80 x\x02'
        response = self.client.get(reverse('layer-postgis', args=(self.layer.pk, 0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_content, response.content)

    def test_postgis_features(self):
        self.maxDiff = None
        expected_content = b'\x1aE\n\x08features\x12\r\x12\x02\x00\x00\x18\x01"\x05\t\x80 \x80 \x12\r\x12\x02\x00\x01' \
                           b'\x18\x01"\x05\t\x80 \x80 \x1a\x04name"\x07\n\x05feat1"\x07\n\x05feat2(\x80 x\x02'
        response = self.client.get(reverse('feature-postgis', args=(0, 0, 0)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_content, response.content)
