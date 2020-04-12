from .azz import AzzLexicalSearchFilterFormset as AzzFormset
from .trq import TrqLexicalSearchFilterFormset as TrqFormset

DEFAULT_FORMSET = AzzFormset

def formset_for_lg(lg_code):
    if lg_code == 'azz':
        return AzzFormset
    if lg_code == 'trq':
        return TrqFormset
    
    return DEFAULT_FORMSET