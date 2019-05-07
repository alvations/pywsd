#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD by maximizing similarity
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

"""
WSD by maximizing similarity.
"""

from wn.info import WordNetInformationContent as WordNetIC

from pywsd.tokenize import word_tokenize
from pywsd.utils import lemmatize

wnic_bnc_resnik_add1 = WordNetIC('bnc', resnik=True, add1=True)
wnic_bnc_add1 = WordNetIC('bnc', resnik=False, add1=True)

def similarity_by_path(sense1: "wn.Synset", sense2: "wn.Synset", option: str = "path") -> float:
    """
    Returns maximum path similarity between two senses.

    :param sense1: A synset.
    :param sense2: A synset.
    :param option: String, one of ('path', 'wup', 'lch').
    :return: A float, similarity measurement.
    """
    if option.lower() in ["path", "path_similarity"]: # Path similarities.
        return max(wn.path_similarity(sense1, sense2, if_none_return=0),
                   wn.path_similarity(sense2, sense1, if_none_return=0))
    elif option.lower() in ["wup", "wupa", "wu-palmer", "wu-palmer"]: # Wu-Palmer
        return max(wn.wup_similarity(sense1, sense2, if_none_return=0),
                   wn.wup_similarity(sense2, sense1, if_none_return=0))
    elif option.lower() in ['lch', "leacock-chordorow"]: # Leacock-Chodorow
        if sense1.pos != sense2.pos: # lch can't do diff POS
            return 0
        return wn.lch_similarity(sense1, sense2, if_none_return=0)


def similarity_by_infocontent(sense1: "wn.Synset", sense2: "wn.Synset", option: str) -> float:
    """
    Returns similarity scores by information content.

    :param sense1: A synset.
    :param sense2: A synset.
    :param option: String, one of ('res', 'jcn', 'lin').
    :return: A float, similarity measurement.
    """

    if sense1.pos != sense2.pos: # infocontent sim can't do diff POS.
        return 0

    if option in ['res', 'resnik']:
        if sense1.pos not in wnic_bnc_resnik_add1.ic:
            return 0
        return wn.res_similarity(sense1, sense2, wnic_bnc_resnik_add1)
    #return min(wn.res_similarity(sense1, sense2, wnic.ic(ic)) \
    #             for ic in info_contents)

    elif option in ['jcn', "jiang-conrath"]:
        if sense1.pos not in wnic_bnc_add1.ic:
            return 0
        return wn.jcn_similarity(sense1, sense2, wnic_bnc_add1)

    elif option in ['lin']:
        if sense1.pos not in wnic_bnc_add1.ic:
            return 0
        return wn.lin_similarity(sense1, sense2, wnic_bnc_add1)


def sim(sense1: "wn.Synset", sense2: "wn.Synset", option: str = "path") -> float:
    """
    Calculates similarity based on user's choice.

    :param sense1: A synset.
    :param sense2: A synset.
    :param option: String, one of ('path', 'wup', 'lch', 'res', 'jcn', 'lin').
    :return: A float, similarity measurement.
    """
    option = option.lower()
    if option.lower() in ["path", "path_similarity",
                        "wup", "wupa", "wu-palmer", "wu-palmer",
                        'lch', "leacock-chordorow"]:
        return similarity_by_path(sense1, sense2, option)
    elif option.lower() in ["res", "resnik",
                          "jcn","jiang-conrath",
                          "lin"]:
        return similarity_by_infocontent(sense1, sense2, option)


def max_similarity(context_sentence: str, ambiguous_word: str, option="path",
                   lemma=True, context_is_lemmatized=False, pos=None, best=True) -> "wn.Synset":
    """
    Perform WSD by maximizing the sum of maximum similarity between possible
    synsets of all words in the context sentence and the possible synsets of the
    ambiguous words (see https://ibin.co/4gG9zUlejUUA.png):
    {argmax}_{synset(a)}(\sum_{i}^{n}{{max}_{synset(i)}(sim(i,a))}

    :param context_sentence: String, a sentence.
    :param ambiguous_word: String, a single word.
    :return: If best, returns only the best Synset, else returns a dict.
    """
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    if context_is_lemmatized:
        context_sentence = word_tokenize(context_sentence)
    else:
        context_sentence = [lemmatize(w) for w in word_tokenize(context_sentence)]
    result = {}
    for i in wn.synsets(ambiguous_word, pos=pos):
        result[i] = 0
        for j in context_sentence:
            _result = [0]
            for k in wn.synsets(j):
                _result.append(sim(i,k,option))
            result[i] += max(_result)

    if option in ["res","resnik"]: # lower score = more similar
        result = sorted([(v,k) for k,v in result.items()])
    else: # higher score = more similar
        result = sorted([(v,k) for k,v in result.items()],reverse=True)

    return result[0][1] if best else result