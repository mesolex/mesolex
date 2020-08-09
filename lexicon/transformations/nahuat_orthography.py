import re

from mesolex.utils import transformation

OTHER = [
    '\(', '\)',
]

VOWELS = [
    'a', 'e', 'i', 'o', 'u',
    'á', 'é', 'í', 'ó', 'ú',
    'à', 'è', 'ì', 'ò', 'ù',
]

CONSONANTS = [
    'h',
    'kw', 'w',
    'k',
    'ch', 'x', 'y',
    'tl', 'l',
    'n', 't', 'ts', 's',
    'm', 'p',
    '$',
    '^',
]

EQUIVALENCE_SETS = [
    ["kwa", "qua", "cua"],
    ["kwe", "cue"],
    ["kwi", "cui"],
    # ["ku", "cu", "que"],  ## This is causing problems ... TODO: find out why and fix!
    ["ka", "ca"],
    ["ko", "co"],
    ["ke", "que"],
    ["ki", "qui"],
    ["ts", "tz"],
    # ["se", "ce"],
    # ["si", "ci"],
    ["sa", "za", "ça"],
    ["so", "zo", "ço"],
]

# Unfortunately, we have to assume that all left
# contexts are *negative* lookbehind; otherwise we
# encounter nasty length-related issues.
CONTEXTUAL_EQUIVALENCE_SETS = [
    (
        set(['t']),
        ['se', 'ce'],
        [],
    ),
    (
        set(['t']),
        ['si', 'ci'],
        [],
    ),
    (
        set(['k', 'c', 'q']),
        ["w", "v", "hu", "u"],
        VOWELS,
    ),
    (
        set(['k', 'c', 'q']),
        ["w", "v", "uh", "u"],
        CONSONANTS
    ),
]


def transform_equivalences(query_string, equivalences):
    """
    Apply a substitution to turn any member of an equivalence class
    into the union of all variants of that equivalence class.
    """
    substitution_class = '({composed})'.format(
        composed='|'.join(equivalences)
    )
    return re.sub(re.compile(substitution_class), substitution_class, query_string)


def transform_equivalences_with_context(query_string, equivalences_with_contexts):
    """
    Like `transform_equivalences`, but applied with the understanding that the preceding
    negative context and following positive context are to be included in the substitution.
    """
    equi_classes = '|'.join(equivalences_with_contexts[1])
    lookbehind_classes = '|'.join(equivalences_with_contexts[0])
    lookahead_classes = '|'.join(equivalences_with_contexts[2])
    substitution_class = '(?<!{lookbehind})({equi})(?=({lookahead}))'.format(
        lookbehind=lookbehind_classes,
        equi=equi_classes,
        lookahead=lookahead_classes,
    )
    target_transformation = '({equi})'.format(equi=equi_classes)
    return re.sub(re.compile(substitution_class), target_transformation, query_string)


@transformation(data_field='nahuat_orthography')
def nahuat_orthography(query_string):
    new_string = query_string

    for equivalences in EQUIVALENCE_SETS:
        new_string = transform_equivalences(new_string, equivalences)

    for equivalences in CONTEXTUAL_EQUIVALENCE_SETS:
        new_string = transform_equivalences_with_context(new_string, equivalences)

    return new_string
