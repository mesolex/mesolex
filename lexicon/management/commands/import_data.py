import logging
import xml.etree.ElementTree as ET

from dateutil.parser import parse
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from lexicon import models

logger = logging.getLogger(__name__)


class Importer(object):
    def __init__(self, input):
        self.input = input

    def _handle_root(self, root):
        raise NotImplementedError()

    def run(self):
        tree = ET.parse(self.input)
        root = tree.getroot()
        return self._handle_root(root)


class AzzImporter(Importer):
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

    def _handle_root(self, root):
        updated_entries = 0
        added_entries = 0

        lx_groups = root.findall('lxGroup')
        total = len(lx_groups)

        for i, lx_group in enumerate(lx_groups):
            (lexical_entry, created, ) = (None, None, )
            entry_kwargs = {}
            defaults = {'language': 'azz'}

            ref = lx_group.find('ref')
            if ref is None:
                logger.error('No ref found for lxGroup at index {i}'.format(i=i))
                continue

            try:
                entry_kwargs['_id'] = int(ref.text)
            except ValueError:
                entry_kwargs['_id'] = ref.text

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

                ostens = sig_group.findall('osten')
                if ostens is not None:
                    osten_string = '; '.join([osten.text for osten in ostens])
                    sig_group_kwargs['ostentive'] = osten_string

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
                    continue

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
                                text=fr_n.text,
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

        return (added_entries, updated_entries, total)


class TrqImporter(Importer):
    def create_simple_string_instances(
        self,
        root_element,
        lexical_entry,
        path,
        model_class,
        additional_lookups={},
        additional_args={},
    ):
        elements = root_element.findall(path)
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
                f"Failed to create {model_class._meta.verbose_name} for lexical entry with ID {lexical_entry._id}, lemma {lexical_entry.lemma}"
            )

    def _handle_root(self, root):
        updated_entries = 0
        added_entries = 0

        entries = root.findall('entry')
        total = len(entries)

        for i, entry_element in enumerate(entries):
            (lexical_entry, created, ) = (None, None, )
            entry_kwargs = {}
            defaults = {'language': 'trq'}

            # get ID for entry
            id_ = entry_element.attrib.get('guid')
            entry_kwargs['_id'] = id_

            # get date
            try:
                defaults['date'] = parse(entry_element.attrib.get('dateModified')
                                         or entry_element.attrib.get('dateCreated'))
            except:
                logger.exception(f"Failed to parse date in entry with id {id_}")
                continue

            # get headword
            try:
                defaults['lemma'] = entry_element.find('./lexical-unit/form[@lang="trq"]/text').text
            except:
                logger.Exception(f"Failed to find headword in entry with id {id_}")
                continue

            # create entry
            try:
                (lexical_entry, created, ) = models.LexicalEntry.objects.update_or_create(
                    defaults=defaults,
                    **entry_kwargs
                )
            except:
                logger.exception(
                    f"Failed to create entry with defaults {defaults}, entry_kwargs {entry_kwargs}",
                )
                # If we don't have a lexical entry, we can't do a whole
                # heck of a lot from hereon in
                continue

            # create citation forms
            self.create_simple_string_instances(
                entry_element,
                lexical_entry,
                './citation/form/text',
                models.Citation,
            )

            # create senses and examples
            # ./sense/
            #   ./sense/gloss/text
            #   OR ./sense/definition/form/text
            #   ./sense/example/form/text/span
            #   ./sense/example/translation/form/text

            senses = entry_element.findall('./sense')
            models.Sense.objects.filter(
                entry=lexical_entry,
            ).delete()
            senses.sort(key=lambda sense: sense.attrib.get('order', 0))

            for i, sense_element in enumerate(senses):
                sense_kwargs = {}

                # NOTE: disjunction on etree elements isn't short-circuiting!
                # TODO: find a properly short-circuiting method to go here
                # to prevent some unnecessary queries
                definition_element = (
                    sense_element.find('./gloss/text')
                    or sense_element.find('./definition/form/text')
                )

                order = int(sense_element.attrib.get('order', i))

                if definition_element is not None:
                    sense_kwargs['definition'] = definition_element.text
                else:
                    continue

                try:
                    sense = models.Sense.objects.create(
                        entry=lexical_entry,
                        order=order,
                        **sense_kwargs,
                    )
                except:
                    logger.exception(
                        f"Failed to create {models.Sense._meta.verbose_name} for lexical entry with ID {lexical_entry._id}, lemma {lexical_entry.lemma}",
                    )
                    continue

                examples = sense_element.findall('example')
                for j, example_element in enumerate(examples):
                    example = models.Example.objects.create(
                        sense=sense,
                        order=j,
                    )

                    ex_text = example_element.find('./form[@lang="es-MX-fonipa-x-emic"]/text/span')
                    if ex_text is not None:
                        try:
                            trq = models.Quote.objects.create(
                                example=example,
                                language='trq',
                                text=ex_text.text,
                            )
                        except:
                            logger.exception(
                                f"Failed to create {models.Quote._meta.verbose_name} for lexical entry with ID {lexical_entry._id}, lemma {lexical_entry.lemma}")
                            continue

                    ex_translation = example_element.find('./translation/form[@lang="es"]/text')
                    if ex_translation is not None:
                        try:
                            es = models.Quote.objects.create(
                                example=example,
                                translation_of=trq,
                                language='es',
                                text=ex_translation.text,
                            )
                        except:
                            logger.exception(
                                f"Failed to create {models.Quote._meta.verbose_name} for lexical entry with ID {lexical_entry._id}, lemma {lexical_entry.lemma}")
                            continue

            if created:
                added_entries += 1
            else:
                updated_entries += 1

        return (added_entries, updated_entries, total)


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    IMPORTERS_BY_CODE = {
        'azz': AzzImporter,
        'trq': TrqImporter,
    }

    def add_arguments(self, parser):
        parser.add_argument('language', type=str)
        parser.add_argument('input', type=str)

    def handle(self, *args, **options):
        input = options['input']
        language = options['language']

        importer = self._importer_for(language)

        (added_entries, updated_entries, total) = importer(input).run() if importer is not None else (0, 0, 0)

        self.stdout.write('\n\nTOTAL: {add} added, {up} updated, {miss} missed'.format(
            add=added_entries,
            up=updated_entries,
            miss=(total - added_entries - updated_entries),
        ))

    def _importer_for(self, language_code):
        return self.IMPORTERS_BY_CODE.get(language_code, None)
