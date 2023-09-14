from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, WKTWriter

from test_vectortiles.test_app.models import FullDataFeature, FullDataLayer

ds = DataSource("/code/src/bd_topo_46.gpkg")
for layer in ds:
    data_layer = FullDataLayer.objects.get_or_create(name=layer.name)[0]
    for feature in layer:
        try:
            geom = feature.geom.geos.transform(4326, clone=True)
            if geom.hasz:
                wkt_w = WKTWriter()
                wkt_w.outdim = 2  # This sets the writer to output 2D WKT
                temp = wkt_w.write(geom)
                geom = GEOSGeometry(temp)  # The 3D geometry
            properties = {field: feature.get(field) for field in layer.fields}
            data = FullDataFeature.objects.create(
                layer=data_layer, geom=geom, properties=properties
            )
        except Exception as exc:
            print(exc)
