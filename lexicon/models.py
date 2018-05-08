from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _


class LexicalEntry(models.Model):
    ref = models.CharField(_("Unique ID"), max_length=64)
    data = JSONField()

    def __str__(self):
        if 'lx' in self.data:
            return self.data['lx']['$']
        else:
            return self.ref or 'Word #%s' % (self.id)
