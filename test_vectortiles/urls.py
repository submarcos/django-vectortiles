from django.contrib import admin
from django.urls import include, path
from django.views.defaults import page_not_found
from rest_framework.routers import SimpleRouter

from test_vectortiles.test_app import views

router = SimpleRouter()
router.register(
    r"features", views.PostGISDRFFeatureViewSet, basename="feature-drf-viewset"
)

urlpatterns = [
    # mapbox related urls
    # feature level
    path("admin/", admin.site.urls),
    path(
        "features/mapbox/tile/<int:z>/<int:x>/<int:y>",
        views.MapboxFeatureView.as_view(),
        name="feature-mapbox",
    ),
    path(
        "features/mapbox/tile/{z}/{x}/{y}",
        page_not_found,
        name="feature-mapbox-pattern",
    ),
    path(
        "features/mapbox/tilejson",
        views.MapboxTileJSONFeatureView.as_view(),
        name="feature-mapbox-tilejson",
    ),
    # layer level
    path(
        "layer/<int:pk>/mapbox/tile/<int:z>/<int:x>/<int:y>",
        views.MapboxLayerView.as_view(),
        name="layer-mapbox",
    ),
    path(
        "layer/<int:pk>/mapbox/tile/{z}/{x}/{y}",
        page_not_found,
        name="layer-mapbox-pattern",
    ),
    path(
        "layer/<int:pk>/mapbox/tilejson",
        views.MapboxTileJSONLayerView.as_view(),
        name="layer-mapbox-tilejson",
    ),
    # postgis related urls
    # feature level
    path(
        "features/postgis/tile/<int:z>/<int:x>/<int:y>",
        views.PostGISFeatureView.as_view(),
        name="feature-postgis",
    ),
    path(
        "features/postgis/drf/listview/tile/<int:z>/<int:x>/<int:y>",
        views.PostGISDRFFeatureView.as_view(),
        name="feature-postgis-drf",
    ),
    path(
        "features/postgis/tile/manual/<int:z>/<int:x>/<int:y>",
        views.PostGISFeatureViewWithManualVectorTileQuerySet.as_view(),
        name="feature-postgis-with-manual-vector-tile-queryset",
    ),
    path(
        "features/postgis/tile/date/<int:z>/<int:x>/<int:y>",
        views.PostGISFeatureWithDateView.as_view(),
        name="feature-date-postgis",
    ),
    path(
        "features/postgis/tile/{z}/{x}/{y}",
        page_not_found,
        name="feature-postgis-pattern",
    ),
    path(
        "features/postgis/tilejson",
        views.PostGISTileJSONFeatureView.as_view(),
        name="feature-postgis-tilejson",
    ),
    # layer level
    path(
        "layer/<int:pk>/postgis/tile/<int:z>/<int:x>/<int:y>",
        views.PostGISLayerView.as_view(),
        name="layer-postgis",
    ),
    path(
        "layer/<int:pk>/postgis/tile/{z}/{x}/{y}",
        page_not_found,
        name="layer-postgis-pattern",
    ),
    path(
        "layer/<int:pk>/postgis/tilejson",
        views.PostGISTileJSONLayerView.as_view(),
        name="layer-postgis-tilejson",
    ),
    path("", include(router.urls)),
    path("", views.IndexView.as_view(), name="index"),
]
