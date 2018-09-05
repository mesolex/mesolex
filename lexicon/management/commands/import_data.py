from dateutil.parser import parse
import xml.etree.ElementTree as ET
from xmljson import parker as xml_parser

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from lexicon import models


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    def add_arguments(self, parser):
        parser.add_argument('input', type=str)

    def handle(self, *args, **options):
        input = options['input']

        tree = ET.parse(input)
        root = tree.getroot()

        updated_entries = 0
        added_entries = 0
        errors = 0
        error_messages = []

        for lx_group in root.getchildren():
            (lexical_entry, created, ) = (None, None, )
            try:
                data = xml_parser.data(lx_group)

                entry_kwargs = {}
                defaults = {}

                if 'ref' not in data:
                    return False  # ref is obligatory
                if isinstance(data['ref'], list):
                    entry_kwargs['_id'] = data['ref'][0]
                else:
                    entry_kwargs['_id'] = data['ref']

                if 'lx' not in data:
                    return False  # lx is obligatory
                if isinstance(data['lx'], list):
                    entry_kwargs['lemma'] = data['lx'][0]
                else:
                    entry_kwargs['lemma'] = data['lx']

                if 'dt' in data:
                    defaults['date'] = parse(
                        data['dt'][0] if isinstance(data['dt'], list) else data['dt']
                    )

                (lexical_entry, created, ) = (models.LexicalEntryTEI.objects.update_or_create(
                    **entry_kwargs,
                    defaults=defaults,
                ))

                if 'lx_var' in data:
                    lx_vars = data['lx_var'] if isinstance(data['lx_var'], list) else [data['lx_var']]
                    models.Geo.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for lx_var in lx_vars:
                        models.Geo.objects.create(
                            entry=lexical_entry,
                            value=lx_var,
                        )

                if 'lx_cita' in data:
                    lx_citas = data['lx_cita'] if isinstance(data['lx_cita'], list) else [data['lx_cita']]
                    models.Citation.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for lx_cita in lx_citas:
                        models.Citation.objects.create(
                            entry=lexical_entry,
                            value=lx_cita,
                        )

                if 'lx_alt' in data:
                    lx_alts = data['lx_alt'] if isinstance(data['lx_alt'], list) else [data['lx_alt']]
                    models.Variant.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for lx_alt in lx_alts:
                        models.Variant.objects.create(
                            entry=lexical_entry,
                            value=lx_alt,
                        )

                if 'sem' in data:
                    sems = data['sem'] if isinstance(data['sem'], list) else [data['sem']]
                    models.Root.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for sem in sems:
                        models.Category.objects.create(
                            entry=lexical_entry,
                            value=sem,
                        )

                if 'raiz' in data:
                    raizs = data['raiz'] if isinstance(data['raiz'], list) else [data['raiz']]
                    models.Root.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for raiz in raizs:
                        models.Root.objects.create(
                            entry=lexical_entry,
                            value=raiz,
                        )

                if 'raiz2' in data:
                    raiz2s = data['raiz2'] if isinstance(data['raiz2'], list) else [data['raiz2']]
                    models.Root.objects.filter(
                        entry=lexical_entry,
                        type='compound',
                    ).delete()
                    for raiz2 in raiz2s:
                        models.Root.objects.create(
                            entry=lexical_entry,
                            value=raiz,
                            type='compound',
                        )

                if 'glosa' in data:
                    glosas = data['glosa'] if isinstance(data['glosa'], list) else [data['glosa']]
                    models.Gloss.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for glosa in glosas:
                        models.Gloss.objects.create(
                            entry=lexical_entry,
                            value=glosa,
                        )

                if 'nota' in data:
                    notas = data['nota'] if isinstance(data['nota'], list) else [data['nota']]
                    models.Note.objects.filter(
                        type='note',
                        entry=lexical_entry,
                    ).delete()
                    for nota in notas:
                        models.Note.objects.create(
                            type='note',
                            entry=lexical_entry,
                            value=nota,
                        )

                if 'nsem' in data:
                    nsems = data['nsem'] if isinstance(data['nsem'], list) else [data['nsem']]
                    models.Note.objects.filter(
                        type='semantics',
                        entry=lexical_entry,
                    ).delete()
                    for nsem in nsems:
                        models.Note.objects.create(
                            type='semantics',
                            entry=lexical_entry,
                            value=nsem,
                        )

                if 'nmorf' in data:
                    nmorfs = data['nmorf'] if isinstance(data['nmorf'], list) else [data['nmorf']]
                    models.Note.objects.filter(
                        type='morphology',
                        entry=lexical_entry,
                    ).delete()
                    for nmorf in nmorfs:
                        models.Note.objects.create(
                            type='morphology',
                            entry=lexical_entry,
                            value=nmorf,
                        )

                if 'catgrGroup' in data:
                    catgr_groups = data['catgrGroup'] if isinstance(data['catgrGroup'], list) else [data['catgrGroup']]
                    models.GrammarGroup.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for catgr_group in catgr_groups:
                        catgr_group_kwargs = {}
                        misc_data = {}

                        if 'catgr' in catgr_group:
                            catgr_group_kwargs['part_of_speech'] = catgr_group['catgr']

                        if 'inflGroup' in catgr_group:
                            infl_group = catgr_group['inflGroup']
                            if 'infl' in infl_group:
                                catgr_group_kwargs['inflectional_type'] = infl_group['infl']

                            if 'plural' in infl_group:
                                misc_data['plural'] = infl_group['plural']

                        if 'diag' in catgr_group:
                            misc_data['diag'] = catgr_group['diag']

                        models.GrammarGroup.objects.create(
                            entry=lexical_entry,
                            misc_data=misc_data,
                            **catgr_group_kwargs,
                        )

                if 'sigGroup' in data:
                    sig_groups = data['sigGroup'] if isinstance(data['sigGroup'], list) else [data['sigGroup']]
                    models.Sense.objects.filter(
                        entry=lexical_entry,
                    ).delete()
                    for i, sig_group in enumerate(sig_groups):
                        sig_group_kwargs = {}
                        if 'sig' in sig_group:
                            sig_group_kwargs['definition'] = sig_group['sig']
                        if 'sig_var' in sig_group:
                            sig_group_kwargs['geo'] = sig_group['sig_var']
                        sense = models.Sense.objects.create(
                            entry=lexical_entry,
                            order=i,
                            **sig_group_kwargs,
                        )

                        if 'fr_nGroup' in sig_group:
                            fr_n_groups = sig_group['fr_nGroup'] if isinstance(sig_group['fr_nGroup'], list) else [sig_group['fr_nGroup']]
                            for j, fr_n_group in enumerate(fr_n_groups):
                                example_kwargs = {}
                                if 'fr_var' in fr_n_group:
                                    example_kwargs['geo'] = fr_n_group['fr_var']
                                example = models.Example.objects.create(
                                    sense=sense,
                                    order=j,
                                    **example_kwargs
                                )

                                if 'fr_n' in fr_n_group:
                                    azz = models.Quote.objects.create(
                                        example=example,
                                        language='azz',
                                        text=fr_n_group['fr_n']
                                    )

                                if 'fr_e' in fr_n_group:
                                    models.Quote.objects.create(
                                        example=example,
                                        translation_of=azz,
                                        language='es',
                                        text=fr_n_group['fr_e']
                                    )

                if created:
                    self.stdout.write('.', ending='')
                    added_entries += 1
                else:
                    self.stdout.write('u', ending='')
                    updated_entries += 1
            except Exception as e:
                self.stdout.write('E', ending='')
                errors += 1
                error_messages.append(str(e))

        if error_messages:
            self.stderr.write('\n\n'.join(error_messages))

        self.stdout.write('\n\nTOTAL: %s added, %s updated, %s errors' % (
            added_entries, updated_entries, errors,
        ))
