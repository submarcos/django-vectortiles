from django.test import TestCase
import mercantile
from vectortiles.postgis.functions import MakeEnvelope

from test_vectortiles.test_app.models import Feature


class MakeEnvelopeTestCase(TestCase):
    def test_implicitely_transform_to_base_srid(self):
        expected_transform = "ST_Transform(ST_MAKEENVELOPE(-20037508.342789244, -20037508.342789244, 20037508.342789244, 20037508.342789244, 3857), 4326)"

        features = Feature.objects.filter(geom__intersects=MakeEnvelope(*mercantile.xy_bounds(0, 0, 0), 3857))

        self.assertIn(expected_transform, str(features.query))
