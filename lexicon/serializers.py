from rest_framework import serializers

from . import models


class LexicalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LexicalEntry
        fields = ('ref', 'headword', 'data', )
