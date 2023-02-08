from django.test import TestCase

from vectortiles.mixins import BaseTileJSONMixin, BaseVectorTileMixin


class BaseVectorTileMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseVectorTileMixin()
            instance.get_tile(0, 0, 0)


class BaseTileJSONMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseTileJSONMixin()
            instance.get_vector_layers()
