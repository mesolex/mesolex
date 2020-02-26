from .azz import LexicalSearchFilterFormset as AzzFormset

DEFAULT_FORMSET = AzzFormset

def formset_for_lg(lg_code):
    if lg_code == 'azz':
        return AzzFormset
    
    return DEFAULT_FORMSET