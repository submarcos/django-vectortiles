from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GinIndex
from django.core.serializers.json import DjangoJSONEncoder


class Layer(models.Model):
    name = models.CharField(max_length=250, unique=True)
    attribution = models.CharField(max_length=250, default="", blank=True)
    description = models.TextField(blank=True)
    min_zoom = models.PositiveSmallIntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=22)

    def __str__(self):
        return self.name


class Feature(models.Model):
    geom = models.GeometryField(srid=4326)
    name = models.CharField(max_length=250)
    layer = models.ForeignKey(
        Layer, on_delete=models.CASCADE, related_name="features", null=True, blank=True
    )
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("id",)


class FullDataLayer(models.Model):
    name = models.CharField(max_length=250, unique=True)
    attribution = models.CharField(max_length=250, default="", blank=True)
    description = models.TextField(blank=True)
    include_in_tilejson = models.BooleanField(default=False)
    min_zoom = models.PositiveSmallIntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=22)
    update_datetime = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class FullDataFeature(models.Model):
    geom = models.GeometryField(srid=4326)
    layer = models.ForeignKey(
        FullDataLayer,
        on_delete=models.CASCADE,
        related_name="features",
        null=True,
        blank=True,
    )
    properties = models.JSONField(default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        ordering = ("id",)
        indexes = [
            GinIndex(fields=["properties"], name="feature_properties_gin"),
        ]
