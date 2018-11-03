from rest_framework import permissions, viewsets

from . import models, serializers


class LexicalEntryViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
    )
    serializer_class = serializers.LexicalEntrySerializer
    queryset = models.LexicalEntry.objects.all()
