import json
import xml.etree.ElementTree as ET
from xmljson import badgerfish as bf

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

        for lx_group in root.getchildren():
            lx_group_dict = bf.data(lx_group)
            data = lx_group_dict['lxGroup']
            if isinstance(data['ref'], list):
                ref = data['ref'][0]
            else:
                ref = data['ref']['$']
            (lexical_entry, created, ) = (models.LexicalEntry.objects.update_or_create(
                ref=ref,
                defaults={
                    'data': data,
                }
            ))

            if created:
                added_entries += 1
            else:
                updated_entries += 1

        self.stdout.write('Added %s entries, updated %s' % (
            added_entries, updated_entries,
        ))
