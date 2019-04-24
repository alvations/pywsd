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

#from nltk.corpus import wordnet as wn
#from nltk.corpus import wordnet_ic as wnic
from wn.info import WordNetInformationContent as WordNetIC

from pywsd.tokenize import word_tokenize
from pywsd.utils import lemmatize

wnic_bnc_resnik_add1 = WordNetIC('bnc', resnik=True, add1=True)
wnic_bnc_add1 = WordNetIC('bnc', resnik=False, add1=True)

def similarity_by_path(sense1, sense2, option="path"):
    """ Returns maximum path similarity between two senses. """
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

def similarity_by_infocontent(sense1, sense2, option):
    """ Returns similarity scores by information content. """
    if sense1.pos != sense2.pos: # infocontent sim can't do diff POS.
        return 0

    info_contents = ['ic-bnc-add1.dat', 'ic-bnc-resnik-add1.dat',
                     'ic-bnc-resnik.dat', 'ic-bnc.dat',

                     'ic-brown-add1.dat', 'ic-brown-resnik-add1.dat',
                     'ic-brown-resnik.dat', 'ic-brown.dat',

                     'ic-semcor-add1.dat', 'ic-semcor.dat',

                     'ic-semcorraw-add1.dat', 'ic-semcorraw-resnik-add1.dat',
                     'ic-semcorraw-resnik.dat', 'ic-semcorraw.dat',

                     'ic-shaks-add1.dat', 'ic-shaks-resnik.dat',
                     'ic-shaks-resnink-add1.dat', 'ic-shaks.dat',

                     'ic-treebank-add1.dat', 'ic-treebank-resnik-add1.dat',
                     'ic-treebank-resnik.dat', 'ic-treebank.dat']

    if option in ['res', 'resnik']:
        return wn.res_similarity(sense1, sense2, wnic_bnc_resnik_add1)
    #return min(wn.res_similarity(sense1, sense2, wnic.ic(ic)) \
    #             for ic in info_contents)

    elif option in ['jcn', "jiang-conrath"]:
        return wn.jcn_similarity(sense1, sense2, wnic_bnc_add1)

    elif option in ['lin']:
        return wn.lin_similarity(sense1, sense2, wnic_bnc_add1)

def sim(sense1, sense2, option="path"):
    """ Calculates similarity based on user's choice. """
    option = option.lower()
    if option.lower() in ["path", "path_similarity",
                        "wup", "wupa", "wu-palmer", "wu-palmer",
                        'lch', "leacock-chordorow"]:
        return similarity_by_path(sense1, sense2, option)
    elif option.lower() in ["res", "resnik",
                          "jcn","jiang-conrath",
                          "lin"]:
        return similarity_by_infocontent(sense1, sense2, option)

def max_similarity(context_sentence, ambiguous_word, option="path",
                   lemma=True, context_is_lemmatized=False, pos=None, best=True):
    """
    Perform WSD by maximizing the sum of maximum similarity between possible
    synsets of all words in the context sentence and the possible synsets of the
    ambiguous words (see http://goo.gl/XMq2BI):
    {argmax}_{synset(a)}(\sum_{i}^{n}{{max}_{synset(i)}(sim(i,a))}
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
    if best: return result[0][1];
    return result

'''
bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']
ans = max_similarity(bank_sents[0], 'bank', pos="n", option="res")
print ans
print ans[0][1].definition
'''
