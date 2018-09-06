from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Prefetch
from django.utils.translation import gettext as _


class ValidEntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(
            sense__isnull=True
        ).prefetch_related(
            'variant_set',
            'citation_set',
            'gloss_set',
            'grammargroup_set',
            'category_set',
            'note_set',
        ).prefetch_related(Prefetch(
            'root_set',
            queryset=Root.objects.filter(type__exact='compound'),
            to_attr='root_compound',
        )).prefetch_related(Prefetch(
            'root_set',
            queryset=Root.objects.exclude(type__exact='compound'),
            to_attr='root_simple',
        )).prefetch_related(Prefetch(
            'note_set',
            queryset=Note.objects.filter(type__exact='morphology'),
            to_attr='notes_morphology',
        )).prefetch_related(Prefetch(
            'note_set',
            queryset=Note.objects.filter(type__exact='semantics'),
            to_attr='notes_semantics',
        )).prefetch_related(Prefetch(
            'note_set',
            queryset=Note.objects.filter(type__exact='note'),
            to_attr='notes_general',
        )).prefetch_related(Prefetch(
            'sense_set',
            queryset=Sense.objects.prefetch_related(Prefetch(
                'example_set',
                queryset=Example.objects.prefetch_related(Prefetch(
                    'quote_set',
                    queryset=Quote.objects.prefetch_related(
                        'translations',
                    ).filter(
                        language__exact='azz'
                    ),
                    to_attr='azz_quotes',
                ))
            ))
        ))


class LexicalEntry(models.Model):
    objects = models.Manager()
    valid_entries = ValidEntryManager()

    # <entry xml:id="{ref}">
    _id = models.CharField(_("Identificación única"), max_length=64)

    # <form type="lemma"><orth>
    lemma = models.CharField(
        _("Entrada"),
        max_length=256,
        db_index=True,
    )

    date = models.DateField(
        blank=True,
        null=True,
    )

    # includes:
    # - rdp_int
    # <xr mesolex:type="compound">
    # <date mesolex:type="review">
    # <ref type="corpus">
    # <xr mesolex:type="{{ sem_dict.type }}">
    misc_data = JSONField(
        blank=True,
        null=True,
    )

    # @property
    # def simple_roots(self):
    #     return self.root_set.exclude(type='compound')
    #
    # @property
    # def compound_roots(self):
    #     return self.root_set.filter(type='compound')

    def __str__(self):
        return self.lemma or self.ref or 'Word #%s' % (self.id)


class AbstractSimpleStringValue(models.Model):
    value = models.CharField(max_length=256, db_index=True)
    entry = models.ForeignKey(
        LexicalEntry,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.value


class Geo(AbstractSimpleStringValue):
    # <usg type="geo">
    pass


class Citation(AbstractSimpleStringValue):
    # <form mesolex:type="citation" type="simple"><orth>
    pass


class Variant(AbstractSimpleStringValue):
    # <form type="variant"><orth>
    pass


class Root(AbstractSimpleStringValue):
    # <etym type="root">
    type = models.CharField(
        max_length=64,
        blank=True,
    )


class Gloss(AbstractSimpleStringValue):
    # <gloss>
    pass


class Note(AbstractSimpleStringValue):
    # <note>
    # <note type="semantics">
    # <note type="morphology">
    value = models.TextField()
    type = models.CharField(max_length=64)


class Category(AbstractSimpleStringValue):
    # <usg type="category">
    pass


class GrammarGroup(models.Model):
    # <gramGrp>
    entry = models.ForeignKey(
        LexicalEntry,
        on_delete=models.CASCADE,
    )

    # <pos>
    part_of_speech = models.CharField(
        max_length=256,
        blank=True,
    )

    # <iType>
    inflectional_type = models.CharField(
        max_length=256,
        blank=True,
    )

    # includes plural class, affix collocations
    misc_data = JSONField(
        blank=True,
        null=True,
    )


class Sense(models.Model):
    # <sense>
    entry = models.ForeignKey(
        LexicalEntry,
        on_delete=models.CASCADE,
    )

    order = models.PositiveIntegerField()

    # <def xml:lang="es">
    definition = models.TextField(
        blank=True,
    )

    # <usg type="geo">
    geo = models.CharField(
        max_length=64,
        blank=True,
    )


class Example(models.Model):
    sense = models.ForeignKey(
        Sense,
        on_delete=models.CASCADE,
    )

    order = models.PositiveIntegerField()

    # <usg type="geo">
    geo = models.CharField(
        max_length=64,
        blank=True,
    )

    # <ptr mesolex:type="au" cRef="{{ cit.au }}" />
    # <ptr mesolex:type="son" cRef="{{ cit.son }}" />
    # <ptr mesolex:type="fuente" cRef="{{ cit.fuente }}" />
    pointers = JSONField(
        null=True,
        blank=True,
    )


class Quote(models.Model):
    example = models.ForeignKey(
        Example,
        on_delete=models.CASCADE,
    )
    translation_of = models.ForeignKey(
        'Quote',
        on_delete=models.CASCADE,
        null=True,
        related_name='translations',
    )

    # <quote xml:lang="{language}">{text}
    language = models.CharField(
        max_length=64,
        blank=True,
    )
    text = models.TextField(
        blank=True,
    )
