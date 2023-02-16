from rest_framework.response import Response
from rest_framework.views import APIView

from vectortiles.mixins import BaseVectorTileView
from vectortiles.rest_framework.renderers import MVTRenderer


class MVTAPIView(BaseVectorTileView, APIView):
    renderer_classes = (MVTRenderer,)

    def get(self, request, z, x, y, *args, **kwargs):
        z, x, y = int(z), int(x), int(y)
        content, status = self.get_content_status(z, x, y)
        return Response(content, status=status)
