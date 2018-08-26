from rest_framework import viewsets

from . import models, serializers


class LexicalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LexicalEntrySerializer
    queryset = models.LexicalEntry.objects.all()



class LexicalEntryTEIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LexicalEntryTEISerializer
    queryset = models.LexicalEntryTEI.objects.all()
