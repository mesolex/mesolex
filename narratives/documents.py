from django_elasticsearch_dsl import DocType, Index, fields

from .models import SoundMetadata


sound_metadata = Index('sound_metadata')
sound_metadata.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@sound_metadata.doc_type
class SoundMetadataDocument(DocType):
    descrip = fields.TextField(analyzer='spanish')

    class Meta:
        model = SoundMetadata
