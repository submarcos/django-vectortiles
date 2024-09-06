from django.test import TestCase

from test_vectortiles.test_app.models import Feature
from vectortiles.backends import BaseVectorLayerMixin


class BaseVectorLayerMixinTestCase(TestCase):
    def test_raise_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            instance = BaseVectorLayerMixin()
            instance.get_tile(0, 0, 0)

    def test_get_description_return_description_by_default(self):
        instance = BaseVectorLayerMixin()
        self.assertEqual(instance.get_description(), instance.description)

    def test_get_layer_fields_return_fields_by_default(self):
        instance = BaseVectorLayerMixin()
        self.assertEqual(instance.get_layer_fields(), {})

    def test_tilejson_vector_layer(self):
        instance = BaseVectorLayerMixin()
        self.assertDictEqual(
            instance.get_tilejson_vector_layer(),
            {
                "id": instance.get_id(),
                "description": instance.get_description(),
                "minzoom": instance.get_min_zoom(),
                "maxzoom": instance.get_max_zoom(),
                "fields": instance.get_layer_fields(),
            },
        )

    def test_queryset_is_used(self):
        instance = BaseVectorLayerMixin()
        instance.queryset = Feature.objects.all()
        self.assertEqual(instance.get_queryset(), instance.queryset)
