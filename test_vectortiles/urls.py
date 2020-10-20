from django.urls import path
from test_vectortiles.test_app import views


urlpatterns = [
    path('features/mapbox-tile/<int:z>/<int:x>/<int:y>', views.MapboxFeatureView.as_view(), name="feature-mapbox"),
    path('layer/<int:pk>/mapbox-tile/<int:z>/<int:x>/<int:y>', views.MapboxLayerView.as_view(), name="layer-mapbox"),
    path('features/postgis-tile/<int:z>/<int:x>/<int:y>', views.PostGISFeatureView.as_view(), name="feature-postgis"),
    path('layer/<int:pk>/postgis-tile/<int:z>/<int:x>/<int:y>', views.PostGISLayerView.as_view(), name="layer-postgis"),
]
