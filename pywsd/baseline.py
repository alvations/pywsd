#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Baseline WSD
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

import random

custom_random = random.Random(0)


def random_sense(ambiguous_word: str, pos=None) -> "wn.Synset":
    """
    Returns a random sense.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: A random Synset.
    """

    if pos is None:
        return custom_random.choice(wn.synsets(ambiguous_word))
    else:
        return custom_random.choice(wn.synsets(ambiguous_word, pos))


def first_sense(ambiguous_word: str, pos: str = None) -> "wn.Synset":
    """
    Returns the first sense.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: The first Synset in the wn.synsets(word) list.
    """

    if pos is None:
        return wn.synsets(ambiguous_word)[0]
    else:
        return wn.synsets(ambiguous_word, pos)[0]


def max_lemma_count(ambiguous_word: str) -> "wn.Synset":
    """
    Returns the sense with the highest lemma_name count.
    The max_lemma_count() can be treated as a rough gauge for the
    Most Frequent Sense (MFS), if no other sense annotated corpus is available.
    NOTE: The lemma counts are from the Brown Corpus

    :param ambiguous_word: String, a single word.
    :return: The estimated most common Synset.
    """
    sense2lemmacounts = {}
    for i in wn.synsets(ambiguous_word, pos=None):
        sense2lemmacounts[i] = sum(j.count() for j in i.lemmas())
    return max(sense2lemmacounts, key=sense2lemmacounts.get)
