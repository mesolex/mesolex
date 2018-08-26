from rest_framework import serializers

from . import models


class LexicalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LexicalEntry
        fields = ('ref', 'headword', 'data', )


class GeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Geo
        fields = (
            'value',
        )


class LexicalEntryTEISerializer(serializers.ModelSerializer):
    # geo = serializers.PrimaryKeyRelatedField(
    #     source='geo_set',
    #     many=True,
    #     queryset=models.Geo.objects.all(),
    # )

    geo_set = GeoSerializer(
        required=False,
        many=True,
    )

    class Meta:
        model = models.LexicalEntryTEI
        fields = (
            '_id',
            'lemma',
            'date',
            'misc_data',

            'geo_set',
        )
