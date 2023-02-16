from django.test import TestCase

from vectortiles.mixins import BaseTileJSONView, BaseVectorTileView


class BaseVectorTileMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseVectorTileView()
            instance.get_tile(0, 0, 0)


class BaseTileJSONMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseTileJSONView()
            instance.get_vector_layers()
