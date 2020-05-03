from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import SoundMetadata


@registry.register_document
class SoundMetadataDocument(Document):
    class Index:
        name = 'sound_metadata'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = SoundMetadata

    descrip = fields.TextField(analyzer='spanish')
