# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from collections import defaultdict

######################################################################
# Table of Contents
######################################################################
# - Constants
# - Data Classes
#   - WordNetError
#   - Lemma
#   - Synset
# - WordNet Corpus Reader
# - WordNet Information Content Corpus Reader
# - Similarity Metrics
# - Demo

######################################################################
# Constants
######################################################################

_ENCODING = 'utf8'

#: Positive infinity (for similarity functions)
_INF = 1e300

# Part of speech constants
ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
POS_LIST = [NOUN, VERB, ADJ, ADV]
_FILEMAP = {ADJ: 'adj', ADV: 'adv', NOUN: 'noun', VERB: 'verb'}
_pos_numbers = {NOUN: 1, VERB: 2, ADJ: 3, ADV: 4, ADJ_SAT: 5}
_pos_names = dict(tup[::-1] for tup in _pos_numbers.items())


#: A list of file identifiers for all the fileids used by wordnet.
_FILES = (
    'cntlist.rev',
    'lexnames',
    'index.sense',
    'index.adj',
    'index.adv',
    'index.noun',
    'index.verb',
    'data.adj',
    'data.adv',
    'data.noun',
    'data.verb',
    'adj.exc',
    'adv.exc',
    'noun.exc',
    'verb.exc',
)

MORPHOLOGICAL_SUBSTITUTIONS = {
    NOUN: [
        ('s', ''),
        ('ses', 's'),
        ('ves', 'f'),
        ('xes', 'x'),
        ('zes', 'z'),
        ('ches', 'ch'),
        ('shes', 'sh'),
        ('men', 'man'),
        ('ies', 'y'),
    ],
    VERB: [
        ('s', ''),
        ('ies', 'y'),
        ('es', 'e'),
        ('es', ''),
        ('ed', 'e'),
        ('ed', ''),
        ('ing', 'e'),
        ('ing', ''),
    ],
    ADJ: [('er', ''), ('est', ''), ('er', 'e'), ('est', 'e')],
    ADV: [],
}

MORPHOLOGICAL_SUBSTITUTIONS[ADJ_SAT] = MORPHOLOGICAL_SUBSTITUTIONS[ADJ]


# A table of strings that are used to express verb frames.
VERB_FRAME_STRINGS = (
    None,
    "Something %s",
    "Somebody %s",
    "It is %sing",
    "Something is %sing PP",
    "Something %s something Adjective/Noun",
    "Something %s Adjective/Noun",
    "Somebody %s Adjective",
    "Somebody %s something",
    "Somebody %s somebody",
    "Something %s somebody",
    "Something %s something",
    "Something %s to somebody",
    "Somebody %s on something",
    "Somebody %s somebody something",
    "Somebody %s something to somebody",
    "Somebody %s something from somebody",
    "Somebody %s somebody with something",
    "Somebody %s somebody of something",
    "Somebody %s something on somebody",
    "Somebody %s somebody PP",
    "Somebody %s something PP",
    "Somebody %s PP",
    "Somebody's (body part) %s",
    "Somebody %s somebody to INFINITIVE",
    "Somebody %s somebody INFINITIVE",
    "Somebody %s that CLAUSE",
    "Somebody %s to somebody",
    "Somebody %s to INFINITIVE",
    "Somebody %s whether INFINITIVE",
    "Somebody %s somebody into V-ing something",
    "Somebody %s something with something",
    "Somebody %s INFINITIVE",
    "Somebody %s VERB-ing",
    "It %s that CLAUSE",
    "Something %s INFINITIVE",
)

SENSENUM_RE = re.compile(r'\.[\d]+\.')


class WordNetError(Exception):
    """An exception class for wordnet-related errors."""


def load_exception_map():
    # load the exception file data into memory
    exception_map = {}
    for pos, suffix in _FILEMAP.items():
        exception_map[pos] = {}
        with open(wordnet_dir+'%s.exc' % suffix) as fin:
            for line in fin:
                terms = line.strip().split()
                exception_map[pos][terms[0]] = terms[1:]
    exception_map[ADJ_SAT] = exception_map[ADJ]
    return exception_map


def load_lemma_pos_offset_map():
    lemma_pos_offset_map = defaultdict(dict)
    for suffix in _FILEMAP.values():
        # parse each line of the file (ignoring comment lines)
        with open(wordnet_dir+'index.%s' % suffix) as fin:
            for i, line in enumerate(fin):
                if line.startswith(' '):
                    continue
                _iter = iter(line.split())
                def _next_token():
                    return next(_iter)
                try:
                    # get the lemma and part-of-speech
                    lemma = _next_token()
                    pos = _next_token()
                    # get the number of synsets for this lemma
                    n_synsets = int(_next_token())
                    assert n_synsets > 0
                    # get and ignore the pointer symbols for all synsets of
                    # this lemma
                    n_pointers = int(_next_token())
                    [_next_token() for _ in range(n_pointers)]
                    # same as number of synsets
                    n_senses = int(_next_token())
                    assert n_synsets == n_senses
                    # get and ignore number of senses ranked according to
                    # frequency
                    _next_token()
                    # get synset offsets
                    synset_offsets = [int(_next_token()) for _ in range(n_synsets)]

                # raise more informative error with file name and line number
                except (AssertionError, ValueError) as e:
                    tup = ('index.%s' % suffix), (i + 1), e
                    raise WordNetError('file %s, line %i: %s' % tup)

                # map lemmas and parts of speech to synsets
                lemma_pos_offset_map[lemma][pos] = synset_offsets
                if pos == ADJ:
                    lemma_pos_offset_map[lemma][ADJ_SAT] = synset_offsets
    return lemma_pos_offset_map

wordnet_dir = os.path.dirname(os.path.abspath(__file__)) + '/data/wordnet/'
exception_map = load_exception_map()
lemma_pos_offset_map = load_lemma_pos_offset_map()


__all__ = [
'_ENCODING',
'_INF',
'POS_LIST',
'ADJ', 'ADJ_SAT', 'ADV', 'NOUN', 'VERB',
'_FILEMAP',
'_pos_numbers',
'_pos_names',
'_FILES',
'MORPHOLOGICAL_SUBSTITUTIONS',
'VERB_FRAME_STRINGS',
'SENSENUM_RE',
'wordnet_dir', 'exception_map', 'lemma_pos_offset_map']
