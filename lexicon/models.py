from django.contrib.postgres.fields import JSONField
from django.db import models


class EntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('media_set')


class Entry(models.Model):
    class Meta:
        verbose_name_plural = 'Entries'

    identifier = models.CharField(
        max_length=256,
        unique=True,
        db_index=True,
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
    dataset = models.CharField(max_length=64)
    data = JSONField(
        blank=True,
        null=True,
    )

    objects = EntryManager()


class Searchable(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'Searchable String'

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


class Media(models.Model):
    class Meta:
        verbose_name = 'Media File Link'

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
