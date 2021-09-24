from os import path
from itertools import chain
from nltk import corpus
from query_api.transformations.utils import transformation

PATH_TO_ES_WN = path.join(path.dirname(path.abspath(__file__)), "wn_spa")
WN_ES = corpus.reader.wordnet.WordNetCorpusReader(PATH_TO_ES_WN, None)

@transformation(data_field='es_thesaurus_lookup')
def es_thesaurus_lookup(query_string):
    synonyms = set(
        chain.from_iterable(
            [word.lemma_names() for word in WN_ES.synsets(query_string)]
        )
    )
    synonyms.update(set([query_string]))
    return "|".join(synonyms)