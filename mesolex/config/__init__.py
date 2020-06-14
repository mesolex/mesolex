import os
import yaml

from django.utils.translation import ugettext_lazy

DEFAULT_LANGUAGE = 'azz'
LANGUAGES = {}


def mark_label_leaves(tree):
    """
    Mutates a given nested dictionary ``tree`` to replace all leaves with
    the label "label" with versions wrapped with ``ugettext_lazy``.
    """
    if not (isinstance(tree, dict)):
        return

    for k in tree:
        if k == 'label':
            tree[k] = ugettext_lazy(tree[k])
        
        if isinstance(tree[k], dict):
            mark_label_leaves(tree[k])
    
        if isinstance(tree[k], list):
            for v in tree[k]:
                mark_label_leaves(v)


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "languages.yml"), "r") as languages_yml:
    language_data = yaml.safe_load(languages_yml)
    mark_label_leaves(language_data)

    LANGUAGES = language_data