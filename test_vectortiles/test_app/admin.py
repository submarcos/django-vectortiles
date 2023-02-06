from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from test_vectortiles.test_app.models import Feature


@admin.register(Feature)
class FeatureAdmin(OSMGeoAdmin):
    list_display = ('id', 'name', 'layer', 'date')
    list_filter = ('layer', 'date')
    search_fields = ('name', )
