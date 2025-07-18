from pathlib import Path

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, WKTWriter
from django.core.management import BaseCommand, CommandError

from test_vectortiles.test_app.models import FullDataFeature, FullDataLayer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_path", help="File's path of the geo file to load")

    def handle(self, *args, **options):
        file_path = options.get("file_path")

        if not Path(file_path).exists():
            msg = f"File at {file_path} does not exist."
            raise CommandError(msg)

        ds = DataSource(file_path, encoding="utf-8")

        for layer in ds:
            data_layer, created = FullDataLayer.objects.get_or_create(name=layer.name)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Handle features in '{data_layer}' (created : {created})"
                )
            )

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
                except Exception:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to handle feature '{data}'")
                    )
