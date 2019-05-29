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
        except:
            logger.exception(
                "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                    model=model_class._meta.verbose_name,
                    ref=lexical_entry._id,
                    lx=lexical_entry.lemma,
                )
            )

    def handle(self, *args, **options):
        input = options['input']

        tree = ET.parse(input)
        root = tree.getroot()

        updated_entries = 0
        added_entries = 0

        lx_groups = root.findall('lxGroup')
        total = len(lx_groups)

        for i, lx_group in enumerate(lx_groups):
            (lexical_entry, created, ) = (None, None, )
            entry_kwargs = {}
            defaults = {}

            ref = lx_group.find('ref')
            if ref is None:
                logger.error('No ref found for lxGroup at index {i}'.format(i=i))
                continue
            
            try:
                entry_kwargs['_id'] = int(ref.text)
            except ValueError:
                entra_kwargs['_id'] = ref.text

            lx = lx_group.find('lx')
            if lx is None:
                logger.error('No lx found for lxGroup at index {i}'.format(i=i))
                continue
            defaults['lemma'] = lx.text

            try:
                dt = lx_group.find('dt')
                defaults['date'] = parse(dt.text) if (dt is not None) else None
            except:
                logger.exception(
                    "Failed to parse date in entry with ref {ref}, lx {lx}".format(
                        ref=ref.text,
                        lx=lx.text,
                    )
                )

            try:
                (lexical_entry, created, ) = models.LexicalEntry.objects.update_or_create(
                    defaults=defaults,
                    **entry_kwargs
                )
            except:
                logger.exception(
                    "Failed to create entry with defaults {defaults}, entry_kwargs {entry_kwargs}".format(
                        defaults=defaults,
                        entry_kwargs=entry_kwargs,
                    )
                )
                # If we don't have a lexical entry, we can't do a whole
                # heck of a lot from hereon in
                continue

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
            try:
                models.NonNativeEtymology.objects.bulk_create([
                    models.NonNativeEtymology(
                        type=pres_tipo_group.find('pres_tipo').text,
                        value=pres_tipo_group.find('pres_el').text,
                        entry=lexical_entry,
                    )
                    for pres_tipo_group in pres_tipo_groups
                    if pres_tipo_group.find('pres_tipo') is not None and pres_tipo_group.find('pres_el') is not None
                ])
            except:
                logger.exception(
                    "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                        model=models.NonNativeEtymology._meta.verbose_name,
                        ref=lexical_entry._id,
                        lx=lexical_entry.lemma,
                    )
                )

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

                try:
                    models.GrammarGroup.objects.create(
                        entry=lexical_entry,
                        misc_data=misc_data,
                        **catgr_group_kwargs
                    )
                except:
                    logger.exception(
                        "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                            model=models.GrammarGroup._meta.verbose_name,
                            ref=lexical_entry._id,
                            lx=lexical_entry.lemma,
                        )
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

                try:
                    sense = models.Sense.objects.create(
                        entry=lexical_entry,
                        order=i,
                        **sig_group_kwargs
                    )
                except:
                    logger.exception(
                        "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                            model=models.Sense._meta.verbose_name,
                            ref=lexical_entry._id,
                            lx=lexical_entry.lemma,
                        )
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
                        try:
                            azz = models.Quote.objects.create(
                                example=example,
                                language='azz',
                                text=fr_n.text
                            )
                        except:
                            logger.exception(
                                "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                                    model=models.Quote._meta.verbose_name,
                                    ref=lexical_entry._id,
                                    lx=lexical_entry.lemma,
                                )
                            )

                    fr_e = fr_n_group.find('fr_e')
                    if fr_e is not None:
                        try:
                            models.Quote.objects.create(
                                example=example,
                                translation_of=azz,
                                language='es',
                                text=fr_e.text
                            )
                        except:
                            logger.exception(
                                "Failed to create {model} for lexical entry with ref {ref}, lx {lx}".format(
                                    model=models.Quote._meta.verbose_name,
                                    ref=lexical_entry._id,
                                    lx=lexical_entry.lemma,
                                )
                            )

            if created:
                added_entries += 1
            else:
                updated_entries += 1

        self.stdout.write('\n\nTOTAL: {add} added, {up} updated, {miss} missed'.format(
            add=added_entries,
            up=updated_entries,
            miss=(total - added_entries - updated_entries),
        ))
