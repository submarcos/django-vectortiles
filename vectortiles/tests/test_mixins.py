from django.test import TestCase

from vectortiles.mixins import BaseTileJSONView, BaseVectorTileView


class BaseTileJSONMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseTileJSONView()
            instance.get_layers()
