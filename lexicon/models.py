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
