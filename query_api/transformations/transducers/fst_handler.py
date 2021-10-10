import os
from typing import List
from retrie.trie import Trie
from query_api.transformations.transducers import attapply


def get_nahuat_att_file(flex=True, isoglosses=False, vln=False):
    att_fn = 'in2dic'

    if flex:
        att_fn += '_flex'
    if vln:
        att_fn += '_vln'
    if isoglosses:
        att_fn += '_iso'

    att_fn += '.att'

    att_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'nahuat',
        'att',
        att_fn,
    )

    return att_path

class FSTHandler(object):
    def __init__(self, path_to_att):
        self.path_to_att = path_to_att
        self.fst = attapply.ATTFST(self.path_to_att)

    def generate_forms(self, w: str) -> List[str]:
        """
        Apply the transducer to an input word and get all generated forms.

        :param w: The word input/searched by a user.
        :return: List of forms generated from applying the FST to w.
        """
        return [w[0] for w in self.fst.apply(w)]

    def match(self, w1: str, w2: str) -> bool:
        """
        Apply fst to w1 and check if any of its outputs match w2.

        :param w1: The word input/searched by a user.
        :param w2: A word from the dictionary
        :return: True if one of the transduced forms of w1 is the same as w2.
        """
        return w2 in self.generate_forms(w1)

    def get_pattern(self, w: str) -> str:
        """
        Get an efficient regex pattern matching all generated forms of a
        given input word.

        :param w: The word input/searched by a user.
        :return: A string that can be compiled into a regex.
        """
        forms = self.generate_forms(w)
        trie = Trie()
        for w in forms:
            trie.add(w)
        return trie.pattern()
