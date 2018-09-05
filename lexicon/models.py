from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _


class ValidEntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(
            sense__isnull=True
        )


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

    @property
    def simple_roots(self):
        return self.root_set.exclude(type='compound')

    @property
    def compound_roots(self):
        return self.root_set.filter(type='compound')

    @property
    def senses(self):
        return self.sense_set.order_by('order')

    @property
    def notes_semantics(self):
        return self.note_set.filter(type='semantics')

    @property
    def notes_morphology(self):
        return self.note_set.filter(type='morphology')

    @property
    def notes_general(self):
        return self.note_set.filter(type='note')

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

    @property
    def examples(self):
        return self.example_set.order_by('order')


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

    @property
    def azz_quotes(self):
        return self.quote_set.filter(language='azz')


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
