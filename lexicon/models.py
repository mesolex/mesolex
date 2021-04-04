from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class EntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


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

    class Meta:
        indexes = [
            GinIndex(
                name='ss_value_gin_idx',
                fields=['value'],
                opclasses=['gin_trgm_ops'],
            ),
            GinIndex(
                name='ss_type_tag_gin_idx',
                fields=['type_tag'],
                opclasses=['gin_trgm_ops'],
            ),
        ]


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
