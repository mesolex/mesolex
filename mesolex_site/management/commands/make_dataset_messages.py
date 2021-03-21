import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from mesolex.config import RAW_DATASETS


def labels(tree):
    label_strings = []

    def append_labels(tree):
        if not isinstance(tree, dict):
            return

        for node_label in tree:
            node = tree[node_label]
            if node_label == 'label':
                label_strings.append(node)

            if isinstance(node, dict):
                append_labels(node)

            if isinstance(node, list):
                for child in node:
                    append_labels(child)

    append_labels(tree)
    return label_strings


class Command(BaseCommand):
    help = _('Genere mensajes de traducción para datos de idiomas.')

    def handle(self, *args, **options):
        base_tmpl_path = os.path.join(
            settings.PROJECT_ROOT,
            'mesolex_site',
            'templates',
            'mesolex_site',
        )
        with open(os.path.join(base_tmpl_path, 'dataset_messages.txt'), 'w') as out:
            out.write(
                render_to_string('mesolex_site/commands/make_language_messages.txt', {
                    'translation_strings': labels(RAW_DATASETS)
                })
            )
        
        with open(os.path.join(base_tmpl_path, 'dataset_messages.js'), 'w') as out:
            out.write(
                render_to_string('mesolex_site/commands/make_language_messages.jst', {
                    'translation_strings': labels(RAW_DATASETS)
                })
            )
