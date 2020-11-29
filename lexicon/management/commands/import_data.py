import logging
from collections import defaultdict
import xml.etree.ElementTree as ET

from dateutil.parser import ParserError, parse
from django.core.management.base import BaseCommand
from django.db import transaction
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


class SimpleAzzImporter(Importer):
    def create_searchable_strings(
            self,
            lx_group,
            tag,
            model_class,
            type_tag,
            entry,
            other_data={},
    ):
        elements = lx_group.findall(tag)
        values = [element.text for element in elements]

        model_class.objects.bulk_create([
            model_class(
                value=value,
                entry=entry,
                language='azz',
                type_tag=type_tag,
                other_data=other_data,
            ) for value in values
        ])

        return values

    def initialize_data(self, lx_group, i):
        entry_data = defaultdict(list)

        entry_data['meta'] = {}
        entry_data['roots'] = {}

        # Find and fetch / create entry
        identifier = lx_group.find('ref')
        if identifier is None:
            logger.error('No ref found for lxGroup at index %d', i)
            return (None, None, None)

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier.text,
        )
        entry.language = 'azz'

        return (entry, entry_data, created)

    def process_basic_data(self, lx_group, i, entry, entry_data):
        # Associate basic data and metadata
        date = lx_group.find('dt')
        try:
            if date is not None:
                parsed_date = parse(date.text)
                entry_data['meta']['date'] = parsed_date.isoformat()
        except ParserError:
            logger.error('Invalid date for lxGroup at index %d', i)

        lemma = lx_group.find('lx')
        if lemma is None:
            logger.error('No lx found for lxGroup at index %d', i)
            return (None, 'Not found')

        entry.value = lemma.text
        return (entry, None)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, lx_group, entry, entry_data):
        entry_data['meta']['variant_data'] = self.create_searchable_strings(
            lx_group,
            'lx_var',
            models.SearchableString,
            'variant_data',
            entry,
        )

        entry_data['citation_forms'] = self.create_searchable_strings(
            lx_group,
            'lx_cita',
            models.SearchableString,
            'citation_form',
            entry,
        )

        entry_data['variant_forms'] = self.create_searchable_strings(
            lx_group,
            'lx_alt',
            models.SearchableString,
            'variant_form',
            entry,
        )

        entry_data['categories'] = self.create_searchable_strings(
            lx_group,
            'sem',
            models.SearchableString,
            'category',
            entry,
        )

        entry_data['roots']['simple'] = self.create_searchable_strings(
            lx_group,
            'raiz',
            models.SearchableString,
            'root',
            entry,
            {
                'root_type': 'simple',
            },
        )
        entry_data['roots']['compound'] = self.create_searchable_strings(
            lx_group,
            'raiz2',
            models.SearchableString,
            'root',
            entry,
            {
                'root_type': 'compound',
            },
        )

        entry_data['glosses'] = self.create_searchable_strings(
            lx_group,
            'glosa',
            models.SearchableString,
            'gloss',
            entry,
        )

    def create_notes(self, lx_group, entry, entry_data):
        entry_data['notes'].extend([
            {
                'note_type': 'note',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nota',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'note',
                },
            )
        ])
        entry_data['notes'].extend([
            {
                'note_type': 'semantics',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nsem',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'semantics',
                },
            )
        ])
        entry_data['notes'].extend([
            {
                'note_type': 'morphology',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nmorf',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'morphology',
                },
            )
        ])

    def create_etymologies(self, lx_group, entry, entry_data):
        pres_tipo_groups = lx_group.findall('pres_tipoGroup')
        pres_tipo_values = [
            {
                'type': group.find('pres_tipo').text,
                'value': group.find('pres_el').text,
            } for group in pres_tipo_groups
            if (
                group.find('pres_tipo') is not None
                and group.find('pres_el') is not None
            )
        ]
        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['value'],
                entry=entry,
                language='azz',
                type_tag='non_native_etymology',
                other_data={
                    'type': value['type'],
                },
            ) for value in pres_tipo_values
        ])
        entry_data['non_native_etymologies'].extend(pres_tipo_values)

    def create_grammars(self, lx_group, entry, entry_data):
        catgr_groups = lx_group.findall('catgrGroup')
        catgr_values = []
        for catgr_group in catgr_groups:
            catgr_value = {'other_data': {}}

            catgr = catgr_group.find('catgr')
            if catgr is not None:
                catgr_value['part_of_speech'] = catgr.text

            infl_group = catgr_group.find('inflGroup')
            if infl_group is not None:
                infl = infl_group.find('infl')
                if infl is not None:
                    catgr_value['inflectional_type'] = infl.text

                plural = infl_group.find('plural')
                if plural is not None:
                    catgr_value['other_data']['plural'] = plural.text

            diag = catgr_group.find('diag')
            if diag is not None:
                catgr_value['other_data']['diag'] = diag.text

            catgr_values.append(catgr_value)

        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['part_of_speech'],
                entry=entry,
                language='azz',
                type_tag='part_of_speech',
            ) for value in catgr_values
            if value.get('part_of_speech') is not None
        ])
        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['inflectional_type'],
                entry=entry,
                language='azz',
                type_tag='inflectional_type',
            ) for value in catgr_values
            if value.get('inflectional_type') is not None
        ])
        entry_data['grammar_groups'].extend(catgr_values)

    def create_definitions(self, lx_group, entry, entry_data):
        sig_groups = lx_group.findall('sigGroup')
        sig_values = []
        for sig_group in sig_groups:
            sig_value = {}

            sig = sig_group.find('sig')
            if sig is not None:
                sig_value['sense'] = sig.text

            sig_var = sig_group.find('sig_var')
            if sig_var is not None:
                sig_value['geo'] = sig_var.text

            ostens = sig_group.findall('osten')
            if ostens is not None:
                sig_value['ostentives'] = [
                    osten.text for osten in ostens
                ]

            examples = []
            fr_n_groups = sig_group.findall('fr_nGroup')
            for fr_n_group in fr_n_groups:
                example_value = {}

                fr_var = fr_n_group.find('fr_var')
                if fr_var is not None:
                    example_value['geo'] = fr_var.text

                fr_n = fr_n_group.find('fr_n')
                if fr_n is not None:
                    example_value['original'] = {
                        'text': fr_n.text,
                        'language': 'azz',
                    }

                fr_e = fr_n_group.find('fr_e')
                if fr_e is not None:
                    example_value['translation'] = {
                        'text': fr_e.text,
                        'language': 'es',
                    }

                examples.append(example_value)

            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['original']['text'],
                    entry=entry,
                    language='azz',
                    type_tag='quote_original',
                ) for example in examples
                if example.get('original') is not None
            ])
            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['translation']['text'],
                    entry=entry,
                    language='es',
                    type_tag='quote_translation',
                ) for example in examples
                if example.get('translation') is not None
            ])

            sig_value['examples'] = examples
            sig_values.append(sig_value)

        models.LongSearchableString.objects.bulk_create([
            models.LongSearchableString(
                value=sig_value.get('sense', ''),
                entry=entry,
                language='es',
                type_tag='sense',
                other_data={
                    'geo': sig_value.get('geo'),
                    'ostentives': sig_value.get('ostentives', []),
                },
            ) for sig_value in sig_values
        ])
        entry_data['senses'].extend(sig_values)

    @transaction.atomic
    def process_lx_group(self, lx_group, i):
        (entry, entry_data, created) = self.initialize_data(lx_group, i)
        if any([x is None for x in [entry, entry_data, created]]):
            return None

        # Associate basic data and metadata
        (_, err) = self.process_basic_data(lx_group, i, entry, entry_data)
        if err is not None:
            return err

        # Clean up previously associated search data.
        self.clean_up_associated_data(entry)

        for method in [
                self.create_simple_string_data,
                self.create_notes,
                self.create_etymologies,
                self.create_grammars,
                self.create_definitions,
        ]:
            method(lx_group, entry, entry_data)

        # Save the result
        entry.other_data = entry_data
        entry.save()

        return created

    def _handle_root(self, root):
        lx_groups = root.findall('lxGroup')
        created = 0
        updated = 0

        for i, lx_group in enumerate(lx_groups):
            try:
                created_entry = self.process_lx_group(lx_group, i)
                if created_entry is None:
                    pass
                elif not created_entry:
                    updated += 1
                elif created_entry:
                    created += 1
            except Exception as e:
                logger.error('Error: %s', e)
                continue

        return (created, updated, len(lx_groups))


class SimpleTrqImporter(Importer):
    def create_searchable_strings(
            self,
            entry_el,
            xpath,
            model_class,
            type_tag,
            entry,
            other_data={},
    ):
        elements = entry_el.findall(xpath)
        values = [element.text for element in elements]

        model_class.objects.bulk_create([
            model_class(
                value=value,
                entry=entry,
                language='trq',
                type_tag=type_tag,
                other_data=other_data,
            ) for value in values
        ])

        return values

    def initialize_data(self, entry_el, i):
        entry_data = defaultdict(list)
        entry_data['meta'] = {}

        identifier = entry_el.attrib.get('guid')
        if identifier is None:
            logger.error('No guid found for entry at index %d', i)
            return (None, None, None)

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier,
        )
        entry.language = 'trq'

        return (entry, entry_data, created)

    def process_basic_data(self, entry_el, i, entry, entry_data):
        try:
            entry_data['meta']['date'] = parse(
                entry_el.attrib.get('dateModified')
                or entry_el.attrib.get('dateCreated')
            ).isoformat()
        except Exception:
            logger.exception(
                'Failed to parse date in entry with id %s',
                entry.identifier,
            )

        try:
            entry.value = entry_el.find(
                './lexical-unit/form[@lang="trq"]/text',
            ).text
        except Exception:
            logger.exception(
                'Failed to find headword in entry with id',
                entry.identifier,
            )
            return (None, 'Not found')

        return (entry, None)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, entry_el, entry, entry_data):
        entry_data['citation_forms'] = self.create_searchable_strings(
            entry_el,
            './citation/form/text',
            models.SearchableString,
            'citation_form',
            entry,
        )

    def create_definitions(self, entry_el, entry, entry_data):
        senses = entry_el.findall('./sense')
        senses.sort(key=lambda sense: sense.attrib.get('order', 0))

        # data to return
        sense_values = []

        for sense_element in senses:
            sense_value = {}

            # NOTE: disjunction on etree elements isn't short-circuiting!
            # TODO: find a properly short-circuiting method to go here
            # to prevent some unnecessary queries
            definition_element = (
                sense_element.find('./gloss/text')
                or sense_element.find('./definition/form/text')
            )

            if definition_element is not None:
                sense_value['sense'] = definition_element.text
            else:
                continue

            examples = []
            example_els = sense_element.findall('example')
            for example_el in example_els:
                example_value = {}

                ex_text = example_el.find('./form[@lang="es-MX-fonipa-x-emic"]/text/span')
                if ex_text is not None:
                    example_value['original'] = {
                        'text': ex_text.text,
                        'language': 'trq',
                    }

                ex_translation = example_el.find('./translation/form[@lang="es"]/text')
                if ex_translation is not None:
                    example_value['translation'] = {
                        'text': ex_translation.text,
                        'language': 'es',
                    }

                examples.append(example_value)

            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['original']['text'],
                    entry=entry,
                    language='trq',
                    type_tag='quote_original',
                ) for example in examples
                if example.get('original') is not None
            ])
            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['translation']['text'],
                    entry=entry,
                    language='es',
                    type_tag='quote_translation',
                ) for example in examples
                if example.get('translation') is not None
            ])

            sense_value['examples'] = examples
            sense_values.append(sense_value)

        models.LongSearchableString.objects.bulk_create([
            models.LongSearchableString(
                value=sense_value.get('sense', ''),
                entry=entry,
                language='es',
                type_tag='sense',
                other_data={},
            ) for sense_value in sense_values
        ])
        entry_data['senses'].extend(sense_values)

    @transaction.atomic
    def process_entry(self, entry_el, i):
        (entry, entry_data, created) = self.initialize_data(entry_el, i)
        if any([x is None for x in [entry, entry_data, created]]):
            return None

        (_, err) = self.process_basic_data(entry_el, i, entry, entry_data)
        if err is not None:
            return err

        self.clean_up_associated_data(entry)

        for method in [
                self.create_simple_string_data,
                self.create_definitions,
        ]:
            method(entry_el, entry, entry_data)

        entry.other_data = entry_data
        entry.save()

        return created

    def _handle_root(self, root):
        entries = root.findall('entry')
        created = 0
        updated = 0

        for i, entry_el in enumerate(entries):
            try:
                created_entry = self.process_entry(entry_el, i)
                if created_entry is None:
                    pass
                elif not created_entry:
                    updated += 1
                elif created_entry:
                    created += 1
            except Exception as e:
                logger.error('Error: %s', e)
                continue

        return (created, updated, len(entries))


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    IMPORTERS_BY_CODE = {
        'azz': AzzImporter,
        'trq': TrqImporter,
        'simple_azz': SimpleAzzImporter,
        'simple_trq': SimpleTrqImporter,
    }

    def add_arguments(self, parser):
        parser.add_argument('language', type=str)
        parser.add_argument('input', type=str)

    def handle(self, *args, **options):
        input = options['input']
        language = options['language']

        importer = self._importer_for(language)

        (added_entries, updated_entries, total) = (
            importer(input).run()
            if importer is not None
            else (0, 0, 0)
        )

        self.stdout.write('\n\nTOTAL: {add} added, {up} updated, {miss} missed'.format(
            add=added_entries,
            up=updated_entries,
            miss=(total - added_entries - updated_entries),
        ))

    def _importer_for(self, language_code):
        return self.IMPORTERS_BY_CODE.get(language_code, None)
