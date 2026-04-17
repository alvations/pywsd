#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD by maximizing similarity
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

"""WSD by maximizing similarity."""

from pywsd._wordnet import wn
from pywsd.tokenize import word_tokenize
from pywsd.utils import lemmatize


def similarity_by_path(sense1, sense2, option: str = "path") -> float:
    """
    Returns maximum path similarity between two senses.

    :param option: One of ('path', 'wup', 'lch').
    """
    opt = option.lower()
    if opt in ("path", "path_similarity"):
        return wn.path_similarity(sense1, sense2)
    if opt in ("wup", "wupa", "wu-palmer"):
        return wn.wup_similarity(sense1, sense2)
    if opt in ("lch", "leacock-chordorow", "leacock-chodorow"):
        if sense1.pos != sense2.pos:
            return 0
        return wn.lch_similarity(sense1, sense2)
    raise ValueError(f"unknown path-similarity option: {option!r}")


def similarity_by_infocontent(sense1, sense2, option: str) -> float:
    """
    Returns similarity scores by information content.

    :param option: One of ('res', 'jcn', 'lin'). Requires an IC frequency dict
        registered via :func:`pywsd._wordnet.set_ic`.
    """
    if sense1.pos != sense2.pos:
        return 0
    opt = option.lower()
    if opt in ("res", "resnik"):
        return wn.res_similarity(sense1, sense2)
    if opt in ("jcn", "jiang-conrath"):
        return wn.jcn_similarity(sense1, sense2)
    if opt in ("lin",):
        return wn.lin_similarity(sense1, sense2)
    raise ValueError(f"unknown info-content option: {option!r}")


def sim(sense1, sense2, option: str = "path") -> float:
    """
    Calculates similarity based on user's choice.

    :param option: One of ('path', 'wup', 'lch', 'res', 'jcn', 'lin').
    """
    opt = option.lower()
    if opt in ("path", "path_similarity", "wup", "wupa", "wu-palmer",
               "lch", "leacock-chordorow", "leacock-chodorow"):
        return similarity_by_path(sense1, sense2, option)
    if opt in ("res", "resnik", "jcn", "jiang-conrath", "lin"):
        return similarity_by_infocontent(sense1, sense2, option)
    raise ValueError(f"unknown similarity option: {option!r}")


def max_similarity(context_sentence: str, ambiguous_word: str, option="path",
                   lemma=True, context_is_lemmatized=False, pos=None, best=True):
    r"""
    Perform WSD by maximizing the sum of maximum similarity between possible
    synsets of all words in the context sentence and the possible synsets of
    the ambiguous word:

    ``argmax_{synset(a)} sum_i max_{synset(i)} sim(i, a)``

    :return: If ``best``, returns only the best Synset; else a sorted list of
        ``(score, synset)`` tuples.
    """
    ambiguous_word = lemmatize(ambiguous_word)
    if not wn.synsets(ambiguous_word):
        return None
    if context_is_lemmatized:
        context_sentence = word_tokenize(context_sentence)
    else:
        context_sentence = [lemmatize(w) for w in word_tokenize(context_sentence)]

    result = {}
    for i in wn.synsets(ambiguous_word, pos=pos):
        total = 0.0
        for j in context_sentence:
            scores = [0.0]
            for k in wn.synsets(j):
                scores.append(sim(i, k, option))
            total += max(scores)
        result[i] = total

    reverse = option.lower() not in ("res", "resnik")  # res: lower score = more similar
    ranked = sorted(((v, k) for k, v in result.items()),
                    key=lambda x: x[0], reverse=reverse)
    return ranked[0][1] if best else ranked
