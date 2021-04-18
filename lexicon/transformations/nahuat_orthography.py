from lexicon.transformations.transducers import fst_handler
from mesolex.utils import transformation

ORTH_HANDLER = fst_handler.FSTHandler(fst_handler.get_nahuat_att_file())


@transformation(data_field='nahuat_orthography')
def nahuat_orthography(query_string):
    return ORTH_HANDLER.get_pattern(query_string)
