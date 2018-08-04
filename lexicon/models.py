from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _


class ValidEntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(
            data__sigGroup__isnull=True
        )


class LexicalEntry(models.Model):
    ref = models.CharField(_("Identificación única"), max_length=64)
    headword = models.CharField(
        _("Entrada"),
        max_length=256,
        db_index=True,
    )
    data = JSONField()
    objects = models.Manager()
    valid_entries = ValidEntryManager()

    def __str__(self):
        return self.headword or self.ref or 'Word #%s' % (self.id)

    class Meta:
        verbose_name = _('Entrada léxica')
        verbose_name_plural = _('Entradas léxicas')
        ordering = ('headword', )
