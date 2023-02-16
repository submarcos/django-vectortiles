from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from test_vectortiles.test_app.models import (
    Feature,
    FullDataFeature,
    FullDataLayer,
    Layer,
)


@admin.register(Feature)
class FeatureAdmin(OSMGeoAdmin):
    list_display = ("id", "name", "layer", "date")
    list_filter = ("layer", "date")
    search_fields = ("name",)


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "attribution", "min_zoom", "max_zoom")
    search_fields = ("id", "name", "description", "attribution")


@admin.register(FullDataLayer)
class FullDataLayerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "attribution",
        "include_in_tilejson",
        "min_zoom",
        "max_zoom",
    )
    search_fields = ("id", "name", "description", "attribution")


@admin.register(FullDataFeature)
class FulDataFeatureAdmin(OSMGeoAdmin):
    list_display = (
        "id",
        "layer",
    )
    list_filter = ("layer",)
