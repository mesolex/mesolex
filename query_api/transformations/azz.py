from query_api.transformations.transducers import fst_handler
from query_api.transformations.utils import transformation

ORTH_HANDLER = fst_handler.FSTHandler(fst_handler.get_nahuat_att_file(True, True, True))


@transformation(data_field='nahuat_orthography')
def nahuat_orthography(query_string):
    return ORTH_HANDLER.get_pattern(query_string)
