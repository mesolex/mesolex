import re
from mesolex.utils import transformation


@transformation(data_field='neutralize_glottal_stop')
def neutralize_glottal_stop(query_string):
    return re.sub(r'([aeiouAEIOUàèìòùÀÈÌÒÙáéíóúÁÉÍÓÚ])\'?', r'\1\'?', query_string)
