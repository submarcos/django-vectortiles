from hashlib import md5

from django.contrib.gis.db.models.functions import Centroid, Transform
from django.core.cache import cache
from django.db.models import Q
from django.utils.text import slugify

from test_vectortiles.test_app.functions import SimplifyPreserveTopology
from test_vectortiles.test_app.models import Feature, FullDataLayer, Layer
from vectortiles import VectorLayer


class FeatureVectorLayer(VectorLayer):
    model = Feature
    vector_tile_layer_name = "features"
    vector_tile_fields = ("name",)
    vector_tile_queryset_limit = 100


class FeatureLayerVectorLayer(VectorLayer):
    model = Layer
    vector_tile_fields = ("name",)

    def __init__(self, instance):
        self.instance = instance

    def get_tile(self, x, y, z):
        cache_key = md5(
            f"{self.get_vector_tile_layer_id()}-{z}-{x}-{y}".encode()
        ).hexdigest()
        if cache.has_key(cache_key):  # NOQA W601
            return cache.get(cache_key)

        else:
            tile = super().get_tile(x, y, z)
            cache.set(cache_key, tile)
            return tile

    def get_vector_tile_layer_id(self):
        return slugify(self.instance.name)

    def get_vector_tile_layer_name(self):
        return slugify(self.instance.name)

    def get_vector_tile_queryset(self, z, x, y):
        return self.instance.features.all()

    def get_vector_tile_layer_max_zoom(self):
        return self.instance.max_zoom

    def get_vector_tile_layer_min_zoom(self):
        return self.instance.min_zoom

    def get_vector_tile_layer_description(self):
        return self.instance.description


class CityCentroidVectorLayer(FeatureLayerVectorLayer):
    vector_tile_geom_name = "centroid"

    def __init__(self):
        self.instance = Layer.objects.get(name="Cities")

    def get_vector_tile_layer_min_zoom(self):
        return 6

    def get_vector_tile_layer_id(self):
        return "city-centroid"

    def get_vector_tile_layer_name(self):
        return "city-centroid"

    def get_vector_tile_queryset(self, *args, **kwargs):
        return self.instance.features.all().annotate(centroid=Centroid("geom"))


class FeatureLayerFilteredByDateVectorLayer(VectorLayer):
    vector_tile_layer_name = "features"
    vector_tile_fields = ("name",)

    def get_vector_tile_queryset(self, *args, **kwargs):
        return Feature.objects.filter(date="2020-07-07")


class FullDataFeatureVectorLayer(VectorLayer):
    vector_tile_fields = ("properties",)

    def __init__(self, instance):
        self.instance = instance

    def get_tile(self, x, y, z):
        cache_key = md5(
            f"{self.get_vector_tile_layer_id()}-{self.instance.update_datetime}-{z}-{x}-{y}".encode()
        ).hexdigest()
        if cache.has_key(cache_key):  # NOQA W601
            return cache.get(cache_key)

        else:
            tile = super().get_tile(x, y, z)
            cache.set(cache_key, tile, timeout=3600 * 24 * 30)
            return tile

    def get_vector_tile_layer_id(self):
        return slugify(self.instance.name)

    def get_vector_tile_layer_name(self):
        return slugify(self.instance.name)

    def get_vector_tile_queryset(self, z, x, y):
        qs = self.instance.features.all()
        if self.instance.name == "troncon_de_route":
            if z in range(self.get_vector_tile_layer_min_zoom(), 9):
                qs = qs.filter(properties__contains={"nature": "Type autoroutier"})
            elif z in range(9, 12):
                qs = qs.filter(
                    Q(
                        properties__nature__in=[
                            "Type autoroutier",
                            "Route à 2 chaussées",
                            "Bretelle",
                        ]
                    )
                )
            elif z in range(12, 15):
                qs = qs.filter(
                    Q(
                        properties__nature__in=[
                            "Type autoroutier",
                            "Route à 2 chaussées",
                            "Bretelle",
                            "Route à 1 chaussée",
                        ]
                    )
                )
        elif self.instance.name == "zone_de_vegetation":
            if z < 15:
                qs = qs.exclude(
                    properties__nature__in=[
                        "Verger",
                        "Vigne",
                        "Haie",
                        "Lande ligneuse",
                        "Peupleraie",
                        "Bois",
                    ]
                )
        return qs

    def get_vector_tile_layer_max_zoom(self):
        return self.instance.max_zoom

    def get_vector_tile_layer_min_zoom(self):
        return self.instance.min_zoom

    def get_vector_tile_layer_description(self):
        return self.instance.description


class FullDataLayerOptimizeVectorLayer(FullDataFeatureVectorLayer):
    vector_tile_geom_name = "simplified_geom"

    def get_vector_tile_queryset(self, *args, **kwargs):
        qs = super().get_vector_tile_queryset(*args, **kwargs)
        z = args[0]
        simplifications = {
            0: 156543,
            1: 78272,
            2: 39136,
            3: 19568,
            4: 9784,
            5: 4892,
            6: 2446,
            7: 1223,
            8: 611.496,
            9: 305.748,
            10: 152.874,
            11: 76.437,
            12: 38.219,
            13: 19.109,
            14: 9.555,
            15: 4.777,
            16: 2.389,
            17: 1.194,
            18: 0.597,
            19: 0.299,
            20: 0.149,
        }
        return qs.annotate(
            simplified_geom=SimplifyPreserveTopology(
                Transform("geom", 3857), simplifications.get(z)
            )
        )


class RegionVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="region")


class DepartementVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="departement")


class EPCIVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="epci")


class CommuneVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="commune")


class SurfaceHydrographiqueVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="surface_hydrographique")


class VoieFerreeVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="troncon_de_voie_ferree")


class TronconRouteVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="troncon_de_route")

    def get_vector_tile_queryset(self, z, x, y):
        qs = super().get_vector_tile_queryset(z, x, y)

        if z in range(self.get_vector_tile_layer_min_zoom(), 9):
            qs = qs.filter(properties__contains={"nature": "Type autoroutier"})
        elif z in range(9, 12):
            qs = qs.filter(
                Q(
                    properties__nature__in=[
                        "Type autoroutier",
                        "Route à 2 chaussées",
                        "Bretelle",
                    ]
                )
            )
        elif z in range(12, 15):
            qs = qs.filter(
                Q(
                    properties__nature__in=[
                        "Type autoroutier",
                        "Route à 2 chaussées",
                        "Bretelle",
                        "Route à 1 chaussée",
                    ]
                )
            )
        return qs


class BatimentVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="batiment")


class TerrainDeSportVectorLayer(FullDataFeatureVectorLayer):
    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="terrain_de_sport")
