from .azz import AzzLexicalSearchFilterFormset as AzzFormset
from .juxt1235 import Juxt1235LexicalSearchFilterFormset as Juxt1235Formset
from .trq import TrqLexicalSearchFilterFormset as TrqFormset

DEFAULT_FORMSET = AzzFormset


def formset_for_lg(lg_code):
    if lg_code == 'azz':
        return AzzFormset
    if lg_code == 'trq':
        return TrqFormset
    if lg_code == 'juxt1235':
        return Juxt1235Formset
    
    return DEFAULT_FORMSET
