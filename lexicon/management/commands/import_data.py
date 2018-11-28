import logging

from dateutil.parser import parse
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from lexicon import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    def add_arguments(self, parser):
        parser.add_argument('input', type=str)

    def create_simple_string_instances(
        self,
        lx_group,
        tag,
        model_class,
        lexical_entry,
        additional_lookups={},
        additional_args={},
    ):
        elements = lx_group.findall(tag)
        model_class.objects.filter(
            entry=lexical_entry,
            **additional_lookups
        ).delete()
        try:
            model_class.objects.bulk_create([
                model_class(
                    entry=lexical_entry,
                    value=element.text,
                    **additional_args
                ) for element in elements
            ])
        except Exception as e:
            logger.exception(
                "Failed to create %s for lexical entry with ref %s, lx %s:\n%s" % (model_class._meta.verbose_name, lexical_entry._id, lexical_entry.lemma, e,)
            )

    def handle(self, *args, **options):
        input = options['input']

        tree = ET.parse(input)
        root = tree.getroot()

        updated_entries = 0
        added_entries = 0

        for lx_group in root.findall('lxGroup'):
            (lexical_entry, created, ) = (None, None, )
            entry_kwargs = {}
            defaults = {}

            ref = lx_group.find('ref')
            if ref is None:
                return False  # ref is obligatory
            entry_kwargs['_id'] = ref.text

            lx = lx_group.find('lx')
            if lx is None:
                return False  # lx is obligatory
            entry_kwargs['lemma'] = lx.text

            try:
                dt = lx_group.find('dt')
                defaults['date'] = parse(dt.text) if (dt is not None) else None
            except Exception as e:
                logger.exception(
                    "Failed to parse date in entry with ref %s, lx %s: %s" % (ref.text, lx.text, e,)
                )

            try:
                (lexical_entry, created, ) = models.LexicalEntry.objects.update_or_create(
                    defaults=defaults,
                    **entry_kwargs
                )
            except Exception as e:
                logger.exception(
                    "Failed to create entry with ref %s, lx %s: %s" % (ref.text, lx.text, e,)
                )

            self.create_simple_string_instances(
                lx_group,
                'lx_var',
                models.Geo,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'lx_cita',
                models.Citation,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'lx_alt',
                models.Variant,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'sem',
                models.Category,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'raiz',
                models.Root,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'raiz2',
                models.Root,
                lexical_entry,
                additional_lookups={
                    'type': 'compound',
                },
                additional_args={
                    'type': 'compound',
                },
            )

            self.create_simple_string_instances(
                lx_group,
                'glosa',
                models.Gloss,
                lexical_entry,
            )

            self.create_simple_string_instances(
                lx_group,
                'nota',
                models.Note,
                lexical_entry,
                additional_lookups={
                    'type': 'note',
                },
                additional_args={
                    'type': 'note',
                },
            )

            self.create_simple_string_instances(
                lx_group,
                'nsem',
                models.Note,
                lexical_entry,
                additional_lookups={
                    'type': 'semantics',
                },
                additional_args={
                    'type': 'semantics',
                },
            )

            self.create_simple_string_instances(
                lx_group,
                'nmorf',
                models.Note,
                lexical_entry,
                additional_lookups={
                    'type': 'morphology',
                },
                additional_args={
                    'type': 'morphology',
                },
            )

            pres_tipo_groups = lx_group.findall('pres_tipoGroup')
            models.NonNativeEtymology.objects.filter(
                entry=lexical_entry,
            ).delete()
            models.NonNativeEtymology.objects.bulk_create([
                models.NonNativeEtymology(
                    type=pres_tipo_group.find('pres_tipo').text,
                    value=pres_tipo_group.find('pres_el').text,
                    entry=lexical_entry,
                )
                for pres_tipo_group in pres_tipo_groups
                if pres_tipo_group.find('pres_tipo') is not None and pres_tipo_group.find('pres_el') is not None
            ])

            catgr_groups = lx_group.findall('catgrGroup')
            models.GrammarGroup.objects.filter(
                entry=lexical_entry,
            ).delete()
            for catgr_group in catgr_groups:
                catgr_group_kwargs = {}
                misc_data = {}

                catgr = catgr_group.find('catgr')
                if catgr is not None:
                    catgr_group_kwargs['part_of_speech'] = catgr.text

                infl_group = catgr_group.find('inflGroup')
                if infl_group is not None:
                    infl = infl_group.find('infl')
                    if infl is not None:
                        catgr_group_kwargs['inflectional_type'] = infl.text

                    plural = infl_group.find('plural')
                    if plural is not None:
                        misc_data['plural'] = plural.text

                diag = catgr_group.find('diag')
                if diag is not None:
                    misc_data['diag'] = diag.text

                models.GrammarGroup.objects.create(
                    entry=lexical_entry,
                    misc_data=misc_data,
                    **catgr_group_kwargs
                )

            sig_groups = lx_group.findall('sigGroup')
            models.Sense.objects.filter(
                entry=lexical_entry,
            ).delete()
            for i, sig_group in enumerate(sig_groups):
                sig_group_kwargs = {}

                sig = sig_group.find('sig')
                if sig is not None:
                    sig_group_kwargs['definition'] = sig.text

                sig_var = sig_group.find('sig_var')
                if sig_var is not None:
                    sig_group_kwargs['geo'] = sig_var.text

                sense = models.Sense.objects.create(
                    entry=lexical_entry,
                    order=i,
                    **sig_group_kwargs
                )

                fr_n_groups = sig_group.findall('fr_nGroup')
                for j, fr_n_group in enumerate(fr_n_groups):
                    example_kwargs = {}

                    fr_var = fr_n_group.find('fr_var')
                    if fr_var is not None:
                        example_kwargs['geo'] = fr_var.text

                    example = models.Example.objects.create(
                        sense=sense,
                        order=j,
                        **example_kwargs
                    )

                    fr_n = fr_n_group.find('fr_n')
                    if fr_n is not None:
                        azz = models.Quote.objects.create(
                            example=example,
                            language='azz',
                            text=fr_n.text
                        )

                    fr_e = fr_n_group.find('fr_e')
                    if fr_e is not None:
                        models.Quote.objects.create(
                            example=example,
                            translation_of=azz,
                            language='es',
                            text=fr_e.text
                        )

            if created:
                added_entries += 1
            else:
                updated_entries += 1

        self.stdout.write('\n\nTOTAL: %s added, %s updated' % (
            added_entries, updated_entries,
        ))
