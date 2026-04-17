#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Baseline WSD
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

import random

from pywsd._wordnet import wn

custom_random = random.Random(0)


def random_sense(ambiguous_word: str, pos=None):
    """
    Returns a random sense.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: A random Synset.
    """
    return custom_random.choice(wn.synsets(ambiguous_word, pos))


def first_sense(ambiguous_word: str, pos: str = None):
    """
    Returns the first sense.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: The first Synset in the wn.synsets(word) list.
    """
    return wn.synsets(ambiguous_word, pos)[0]


def _synset_freq(ss) -> int:
    """Sum of all sense counts across corpora for the synset."""
    return sum(sum(sense.counts()) for sense in ss.senses())


def max_lemma_count(ambiguous_word: str):
    """
    Returns the sense with the highest lemma_name count.

    A rough gauge for the Most Frequent Sense (MFS) when no annotated corpus
    is available. Counts come from whatever corpora the installed wordnet
    lexicon exposes; if none are present this falls back to ``first_sense``.
    """
    candidates = wn.synsets(ambiguous_word)
    if not candidates:
        return None
    scored = [(_synset_freq(ss), ss) for ss in candidates]
    best = max(scored, key=lambda x: x[0])
    if best[0] == 0:
        return candidates[0]
    return best[1]
