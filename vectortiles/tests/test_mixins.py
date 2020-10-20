from django.test import TestCase
from vectortiles.mixins import BaseVectorTileMixin


class BaseVectorTileMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseVectorTileMixin()
            instance.get_tile(0, 0, 0)
