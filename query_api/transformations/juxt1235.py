import re
from query_api.transformations.utils import transformation


@transformation(data_field='neutralize_glottal_stop')
def neutralize_glottal_stop(value):
    return re.sub(r'([aeiouAEIOUàèìòùÀÈÌÒÙáéíóúÁÉÍÓÚ])\'?', r'\1\'?', value)
