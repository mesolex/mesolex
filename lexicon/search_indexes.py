from haystack import indexes

from lexicon import models


class LexicalEntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    headword = indexes.CharField()
    nmorf = indexes.CharField(model_attr='data')

    def get_model(self):
        return models.LexicalEntry

    def prepare_nmorf(self, obj):
        return obj.nmorf
