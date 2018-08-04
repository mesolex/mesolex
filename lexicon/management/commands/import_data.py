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
                if isinstance(data['ref'], list):
                    ref = data['ref'][0]
                else:
                    ref = data['ref']
                (lexical_entry, created, ) = (models.LexicalEntry.objects.update_or_create(
                    ref=ref,
                    headword=data['lx'],
                    defaults={
                        'data': data,
                    }
                ))

                # # NOTE: the following is an example of how to process
                # # possibly-multiple data contained in the blob, associating
                # # it with a simple model that can be used to associate it
                # # with a lexical entry. This code was written in a draft
                # # that used a LexCitationForm model, subsequently removed.

                # if 'lx_cita' in data:
                #     if isinstance(data['lx_cita'], list):
                #         lx_citas = data['lx_cita']
                #     else:
                #         lx_citas = [data['lx_cita']]
                #
                #     for lx_cita in lx_citas:
                #         if isinstance(lx_cita, str):
                #             (lx_cita_instance, created, ) = (models.LexCitationForm.objects.update_or_create(
                #                 entry=lexical_entry,
                #                 value=lx_cita,
                #             ))
                #
                #             if created:
                #                 added_citations += 1
                #             else:
                #                 updated_citations += 1

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
