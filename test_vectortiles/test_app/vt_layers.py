from hashlib import md5

from django.contrib.gis.db.models.functions import Centroid
from django.core.cache import cache
from django.db.models import FloatField, Q
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.utils.text import slugify

from test_vectortiles.test_app.models import Feature, Layer, FullDataLayer
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

    def get_id(self):
        return slugify(self.instance.name)

    def get_vector_tile_queryset(self, z, x, y):
        return self.instance.features.all()

    def get_max_zoom(self):
        return self.instance.max_zoom

    def get_min_zoom(self):
        return self.instance.min_zoom

    def get_description(self):
        return self.instance.description




class FeatureLayerFilteredByDateVectorLayer(VectorLayer):
    name = "features"
    tile_fields = ("name",)

    def get_vector_tile_queryset(self, *args, **kwargs):
        return Feature.objects.filter(date="2020-07-07")


class FullDataFeatureVectorLayer(VectorLayer):
    def __init__(self, instance):
        self.instance = instance

    def get_tile_fields(self):
        if self.instance.name == "troncon_de_route":
            return ("nature",)
        elif self.instance.name == "batiment":
            return ("hauteur",)
        elif self.instance.name in ("commune", "commune_centre"):
            return (
                "nom",
                "population",
                "chef_lieu_region",
                "chef_lieu_departement",
            )
        elif self.instance.name == "troncon_hydrographique":
            return ("nom", )
        elif self.instance.name == "parc_ou_reserve":
            return ("nom", "nature")
        elif self.instance.name == "departement":
            return ("nom", "code_insee", "code_insee_region")
        elif self.instance.name == "region":
            return ("nom", "code_insee",)
        elif self.instance.name == "troncon_voie_ferree":
            return ("nature", "voies", "etat", "position")
        elif self.instance.name == "surface_hydrographique":
            return ("nature",)
        elif self.instance.name == "terrain_de_sport":
            return ("nature",)
        return ("properties",)

    def get_tile(self, x, y, z):
        cache_key = md5(
            f"{self.get_id()}-{self.instance.update_datetime}-{z}-{x}-{y}".encode()
        ).hexdigest()
        if cache.has_key(cache_key):  # NOQA W601
            return cache.get(cache_key)

        else:
            tile = super().get_tile(x, y, z)
            cache.set(cache_key, tile, timeout=3600 * 24 * 30)
            return tile

    def get_id(self):
        return slugify(self.instance.name)

    def get_vector_tile_queryset(self, z, x, y):
        qs = self.instance.features.all()
        if self.instance.name == "troncon_de_route":
            if z in range(self.get_min_zoom(), 9):
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
            qs = qs.annotate(
                nature=KeyTextTransform(
                    "nature",
                    "properties",
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
        elif self.instance.name == "batiment":
            qs = qs.annotate(
                hauteur=Cast(
                    KeyTextTransform("hauteur", "properties"), output_field=FloatField()
                )
            )
        elif self.instance.name in ("commune", "commune_centre"):
            qs = qs.annotate(
                nom=KeyTextTransform(
                    "nom_officiel",
                    "properties",
                ),
                population=Cast(
                    KeyTextTransform("population", "properties"),
                    output_field=FloatField(),
                ),
                chef_lieu_region=KeyTextTransform(
                    "chef_lieu_de_region",
                    "properties",
                ),
                chef_lieu_departement=KeyTextTransform(
                    "chef_lieu_de_departement",
                    "properties",
                ),
            )
        elif self.instance.name == "troncon_hydrographique":
            qs = qs.exclude(properties__contains={"position_par_rapport_au_sol": "-1", })
            qs = qs.annotate(nom=KeyTextTransform("cpx_toponyme_de_cours_d_eau", "properties"))
        elif self.instance.name == "parc_ou_reserve":
            qs = qs.annotate(nom=KeyTextTransform("toponyme", "properties"),
                             nature=KeyTextTransform("nature", "properties"))
        elif self.instance.name == "departement":
            qs = qs.annotate(nom=KeyTextTransform("nom_officiel", "properties"),
                             code_insee=KeyTextTransform("code_insee", "properties"),
                             code_insee_region=KeyTextTransform("code_insee_de_la_region", "properties"))
        elif self.instance.name == "region":
            qs = qs.annotate(nom=KeyTextTransform("nom_officiel", "properties"),
                             code_insee=KeyTextTransform("code_insee", "properties"))
        elif self.instance.name == "troncon_voie_ferree":
            qs = qs.annotate(nature=KeyTextTransform("nature", "properties"),
                             voies=KeyTextTransform("nombre_de_voies", "properties"),
                             etat=KeyTextTransform("etat_de_l_objet", "properties"),
                             position=KeyTextTransform("position_par_rapport_au_sol", "properties"))
        elif self.instance.name == "surface_hydrographique":
            qs = qs.annotate(nature=KeyTextTransform("nature", "properties"))
        elif self.instance.name == "terrain_de_sport":
            qs = qs.annotate(nature=KeyTextTransform("nature", "properties"))
        return qs

    def get_max_zoom(self):
        return self.instance.max_zoom

    def get_min_zoom(self):
        return self.instance.min_zoom

    def get_description(self):
        return self.instance.description


class CityCentroidVectorLayer(FullDataFeatureVectorLayer):
    geom_field = "centroid"

    def __init__(self):
        self.instance = FullDataLayer.objects.get(name="commune")

    def get_min_zoom(self):
        return 6

    def get_id(self):
        return "commune_centre"

    def get_vector_tile_queryset(self, *args, **kwargs):
        qs = super().get_vector_tile_queryset(*args, **kwargs)
        qs = qs.annotate(centroid=Centroid("geom"))
        return qs
