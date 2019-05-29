from django_elasticsearch_dsl import DocType, Index, fields

from .models import LexicalEntry, Quote


lexical_entry = Index('lexical_entry')
lexical_entry.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@lexical_entry.doc_type
class LexicalEntryDocument(DocType):
    quotations_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )
    quotations_azz = fields.TextField(multi=True)

    def prepare_quotations_es(self, instance):
        return list(
            Quote.objects.filter(example__sense__entry__id=instance.id)
            .filter(language='es')
            .values_list('text', flat=True)
        )
    
    def prepare_quotations_azz(self, instance):
        return list(
                Quote.objects.filter(example__sense__entry__id=instance.id)
                .filter(language='azz')
                .values_list('text', flat=True)
            )

    class Meta:
        model = LexicalEntry
        fields = [
            'lemma',
        ]