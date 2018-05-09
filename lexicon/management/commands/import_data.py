import xml.etree.ElementTree as ET
from xmljson import parker as xml_parser

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from lexicon import models


class Command(BaseCommand):
    help = _("Reads an XML data source file and updates the database.")

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
