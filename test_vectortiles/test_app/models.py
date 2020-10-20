from django.contrib.gis.db import models


class Layer(models.Model):
    name = models.CharField(max_length=250)


class Feature(models.Model):
    geom = models.GeometryField(srid=4326)
    name = models.CharField(max_length=250)
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name='features')
