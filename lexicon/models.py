from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _


class Entry(models.Model):
    identifier = models.CharField(
        max_length=256,
        unique=True,
    )
    parent_entry = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    value = models.CharField(
        max_length=256,
        db_index=True,
    )
    language = models.CharField(max_length=64)
    other_data = JSONField(
        blank=True,
        null=True,
    )


class Searchable(models.Model):
    class Meta:
        abstract = True

    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
    )
    language = models.CharField(max_length=64)
    type_tag = models.CharField(
        max_length=256,
        db_index=True,
    )
    other_data = JSONField(
        blank=True,
        null=True,
    )


class SearchableString(Searchable):
    value = models.CharField(
        max_length=256,
        db_index=True,
    )


class LongSearchableString(Searchable):
    value = models.TextField()


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
    language = models.CharField("Lengua", max_length=64)

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
        return [root for root in self.root_set.all() if root.type != 'compound']

    @property
    def compound_roots(self):
        return [root for root in self.root_set.all() if root.type == 'compound']

    @property
    def notes_general(self):
        return [note for note in self.note_set.all() if note.type == 'note']

    @property
    def notes_morphology(self):
        return [note for note in self.note_set.all() if note.type == 'morphology']

    @property
    def notes_semantics(self):
        return [note for note in self.note_set.all() if note.type == 'semantics']

    @property
    def senses(self):
        return sorted(list(self.sense_set.all()), key=lambda x: x.order)

    def __str__(self):
        return self.lemma or 'Word #%s' % (self.id)

    class Meta:
        verbose_name = 'Lexical entry'
        verbose_name_plural = 'Lexical entries'


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


class Media(models.Model):
    lexical_entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        null=True,
    )
    url = models.URLField()
    mime_type = models.CharField(
        max_length=64,
        default='audio/mpeg',
    )

    def __str__(self):
        return self.url


class Variant(AbstractSimpleStringValue):
    # <form type="variant"><orth>
    pass


class Root(AbstractSimpleStringValue):
    # <etym type="root">
    type = models.CharField(
        max_length=64,
        blank=True,
    )


class NonNativeEtymology(AbstractSimpleStringValue):
    # NOTE: this is specific to the azz dataset's pres_tipoGroup.
    # <etym type="{type}">{value}</etym>
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

    # <usg type="subj">
    ostentive = models.TextField(
        blank=True,
    )

    # <usg type="geo">
    geo = models.CharField(
        max_length=64,
        blank=True,
    )

    @property
    def examples(self):
        return sorted(list(self.example_set.all()), key=lambda x: x.order)


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
    def original_quotes(self):
        return list(self.quote_set.filter(translation_of__isnull=True))


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
