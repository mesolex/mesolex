from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from .utils import (
    get_list_safe,
)


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

    @property
    def nmorf(self):
        return self.data['nmorf'] if 'nmorf' in self.data else None

    @property
    def lex_cita_S(self):
        return get_list_safe(self.data, 'lx_cita')

    @property
    def raiz_S(self):
        return get_list_safe(self.data, 'raiz')

    @property
    def glosa_S(self):
        return get_list_safe(self.data, 'glosa')

    @property
    def nsem_S(self):
        return get_list_safe(self.data, 'nsem')

    @property
    def osten_S(self):
        return get_list_safe(self.data, 'osten')

    @property
    def sigGroup_sig_S(self):
        sigGroup = get_list_safe(self.data, 'sigGroup')
        return ([sig_obj['sig'] for sig_obj in sigGroup
                if isinstance(sig_obj, dict) and 'sig' in sig_obj])

    def _prepare_fr_nGroup_el(self, data, key):
        fr_nGroup = get_list_safe(data, 'fr_nGroup')
        return ([fr_n_obj[key] for fr_n_obj in fr_nGroup
                if isinstance(fr_n_obj, dict) and key in fr_n_obj])

    def _prepare_sigGroup_fr_nGroup_el(self, data, key):
        vals = []
        sigGroup = get_list_safe(data, 'sigGroup')
        for sig_obj in sigGroup:
            vals += self._prepare_fr_nGroup_el(sig_obj, key)
        return vals

    @property
    def sigGroup_fr_nGroup_fr_e_S(self):
        return self._prepare_sigGroup_fr_nGroup_el(self.data, 'fr_e')

    @property
    def sigGroup_fr_nGroup_fr_n_S(self):
        return self._prepare_sigGroup_fr_nGroup_el(self.data, 'fr_n')

    @property
    def fr_nGroup_fr_e_S(self):
        return self._prepare_fr_nGroup_el(self.data, 'fr_e')

    @property
    def fr_nGroup_fr_n_S(self):
        return self._prepare_fr_nGroup_el(self.data, 'fr_n')
