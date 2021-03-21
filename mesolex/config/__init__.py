import os
from copy import deepcopy

import yaml
from django.utils.translation import ugettext_lazy as _

DEFAULT_DATASET = 'azz'
RAW_DATASETS = {}
DATASETS = {}


def mark_label_leaves(tree):
    """
    Mutates a given nested dictionary ``tree`` to replace all leaves with
    the label "label" with versions wrapped with ``ugettext_lazy``.
    """
    if not isinstance(tree, dict):
        return

    for node_label in tree:
        node = tree[node_label]
        if node_label == 'label':
            node = _(node)

        if isinstance(node, dict):
            mark_label_leaves(node)

        if isinstance(node, list):
            for child in node:
                mark_label_leaves(child)


with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'datasets.yml',
        ), 'r') as datasets_yml:
    RAW_DATASETS = yaml.safe_load(datasets_yml)
    DATASETS = deepcopy(RAW_DATASETS)
    mark_label_leaves(DATASETS)
