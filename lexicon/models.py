from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _


class LexicalEntry(models.Model):
    ref = models.CharField(_("Unique ID"), max_length=64)
    headword = models.CharField(_("Headword"), max_length=256)
    data = JSONField()

    def __str__(self):
        return self.headword or self.ref or 'Word #%s' % (self.id)

    class Meta:
        verbose_name = _('Lexical Entry')
        verbose_name_plural = _('Lexical Entries')
        ordering = ('headword', )
