import itertools

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Entry


@registry.register_document
class EntryDocument(Document):
    class Index:
        name = 'entry'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Entry
        fields = [
            'value',
        ]

    quotations_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    quotations_azz = fields.TextField(multi=True)
    quotations_trq = fields.TextField(multi=True)

    definitions_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    ostentives_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    nsem_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    def prepare_definitions_es(self, instance):
        return [sense_dict['sense'] for sense_dict in instance.data.get('senses', [])]

    def prepare_ostentives_es(self, instance):
        return list(
            itertools.chain(
                *[sense.get('ostentives', []) for sense in instance.data.get('senses', [])],
            ),
        )

    def prepare_quotations_es(self, instance):
        return list([
            example['translation'].get('text', '')
            for example in itertools.chain(
                *[sense.get('examples', []) for sense in instance.data.get('senses', [])],
            )
            if example.get('translation') is not None and example['translation']['language'] == 'es'
        ])

    def prepare_quotations_azz(self, instance):
        return list([
            example['original'].get('text', '')
            for example in itertools.chain(
                *[sense.get('examples', []) for sense in instance.data.get('senses', [])],
            )
            if example.get('original') is not None and example['original']['language'] == 'azz'
        ])

    def prepare_quotations_trq(self, instance):
        return list([
            example['original'].get('text', '')
            for example in itertools.chain(
                *[sense.get('examples', []) for sense in instance.data.get('senses', [])],
            )
            if example.get('original') is not None and example['original']['language'] == 'trq'
        ])

    def prepare_nsem_es(self, instance):
        return [
            note['text']
            for note in instance.data.get('notes', [])
            if note['note_type'] == 'semantics'
        ]
