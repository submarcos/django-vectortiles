from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import Func
from django.utils.functional import cached_property


class MakeEnvelope(Func):
    function = "ST_MAKEENVELOPE"
    output_field = GeometryField()


class AsMVTGeom(GeoFunc):
    function = "ST_ASMVTGEOM"

    @cached_property
    def output_field(self):
        return GeometryField(srid=3857)
