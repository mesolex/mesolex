from .azz import AzzLexicalSearchFilterFormset as AzzFormset
from .juxt1235_verb import Juxt1235VerbLexicalSearchFilterFormset as Juxt1235VerbFormset
from .trq import TrqLexicalSearchFilterFormset as TrqFormset

DEFAULT_FORMSET = AzzFormset


def formset_for_dataset(dataset_code):
    if dataset_code == 'azz':
        return AzzFormset
    if dataset_code == 'trq':
        return TrqFormset
    if dataset_code == 'juxt1235_verb':
        return Juxt1235VerbFormset
    
    return DEFAULT_FORMSET
