from django.contrib import admin
from django.urls import include, path
from django.views.defaults import page_not_found
from rest_framework.routers import SimpleRouter

from test_vectortiles.test_app import views

router = SimpleRouter()
router.register(r"features", views.FeatureViewSet, basename="feature-drf-viewset")

urlpatterns = [
    # feature level
    path("admin/", admin.site.urls),
    path(
        "features/tile/<int:z>/<int:x>/<int:y>",
        views.FeatureView.as_view(),
        name="feature",
    ),
    path(
        "features/tile/date/<int:z>/<int:x>/<int:y>",
        views.FeatureWithDateView.as_view(),
        name="feature-date",
    ),
    path(
        "features/tile/{z}/{x}/{y}",
        page_not_found,
        name="feature-pattern",
    ),
    path(
        "features/tilejson",
        views.TileJSONFeatureView.as_view(),
        name="feature-tilejson",
    ),
    # layer level
    path(
        "layer/tile/<int:z>/<int:x>/<int:y>",
        views.LayerView.as_view(),
        name="layer",
    ),
    path(
        "layer/tiles.json",
        views.LayerTileJSONView.as_view(),
        name="layer-tilejson",
    ),
    path(
        "layer/tile/{z}/{x}/{y}",
        page_not_found,
        name="layer-pattern",
    ),
    path("", include(router.urls)),
    path("", views.IndexView.as_view(), name="index"),
]
