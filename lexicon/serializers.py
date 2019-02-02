from rest_framework import serializers

from . import models


class GeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Geo
        fields = (
            'value',
        )


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Media
        fields = (
            'url',
            'mime_type',
        )


class CitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Citation
        fields = (
            'value',
        )


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Variant
        fields = (
            'value',
        )


class RootSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Root
        fields = (
            'value',
        )


class GlossSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gloss
        fields = (
            'value',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'value',
        )


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Note
        fields = (
            'type',
            'value',
        )


class GrammarGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GrammarGroup
        fields = (
            'part_of_speech',
            'inflectional_type',
            'misc_data',
        )


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quote
        fields = (
            'language',
            'text',
        )


class ExampleSerializer(serializers.ModelSerializer):
    quote_set = QuoteSerializer(
        required=False,
        many=True,
    )

    class Meta:
        model = models.Example
        fields = (
            'quote_set',
            'geo',
            'pointers',
        )


class SenseSerializer(serializers.ModelSerializer):
    example_set = ExampleSerializer(
        required=False,
        many=True,
    )

    class Meta:
        model = models.Sense
        fields = (
            'order',
            'definition',
            'geo',
            'example_set',
        )


class LexicalEntrySerializer(serializers.ModelSerializer):
    # geo = serializers.PrimaryKeyRelatedField(
    #     source='geo_set',
    #     many=True,
    #     queryset=models.Geo.objects.all(),
    # )

    geo_set = GeoSerializer(
        required=False,
        many=True,
    )
    citation_set = CitationSerializer(
        required=False,
        many=True,
    )
    variant_set = VariantSerializer(
        required=False,
        many=True,
    )
    root_set = RootSerializer(
        required=False,
        many=True,
    )
    gloss_set = GlossSerializer(
        required=False,
        many=True,
    )
    category_set = CategorySerializer(
        required=False,
        many=True,
    )

    note_set = NoteSerializer(
        required=False,
        many=True,
    )

    grammargroup_set = GrammarGroupSerializer(
        required=False,
        many=True,
    )

    sense_set = SenseSerializer(
        required=False,
        many=True,
    )

    media_set = MediaSerializer(
        required=False,
        many=True,
    )

    class Meta:
        model = models.LexicalEntry
        fields = (
            '_id',
            'lemma',
            'date',
            'misc_data',

            'geo_set',
            'citation_set',
            'variant_set',
            'root_set',
            'gloss_set',
            'category_set',

            'note_set',

            'grammargroup_set',

            'sense_set',

            'media_set',
        )
