#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD by maximizing similarity
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

"""
WSD by maximizing similarity. 
"""

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wnic
from nltk.tokenize import word_tokenize

from utils import lemmatize

def similarity_by_path(sense1, sense2, option="path"):
    """ Returns maximum path similarity between two senses. """
    if option.lower() in ["path", "path_similarity"]: # Path similaritys
        return max(wn.path_similarity(sense1,sense2), 
                   wn.path_similarity(sense1,sense2))
    elif option.lower() in ["wup", "wupa", "wu-palmer", "wu-palmer"]: # Wu-Palmer 
        return wn.wup_similarity(sense1, sense2)
    elif option.lower() in ['lch', "leacock-chordorow"]: # Leacock-Chodorow
        if sense1.pos != sense2.pos: # lch can't do diff POS
            return 0
        return wn.lch_similarity(sense1, sense2)

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
        return wn.res_similarity(sense1, sense2, wnic.ic('ic-bnc-resnik-add1.dat'))
    #return min(wn.res_similarity(sense1, sense2, wnic.ic(ic)) \
    #             for ic in info_contents)

    elif option in ['jcn', "jiang-conrath"]:
        return wn.jcn_similarity(sense1, sense2, wnic.ic('ic-bnc-add1.dat'))
  
    elif option in ['lin']:
        return wn.lin_similarity(sense1, sense2, wnic.ic('ic-bnc-add1.dat'))

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
    for i in wn.synsets(ambiguous_word):
        try:
            if pos and pos != str(i.pos()):
                continue
        except:
            if pos and pos != str(i.pos):
                continue 
        result[i] = sum(max([sim(i,k,option) for k in wn.synsets(j)]+[0]) \
                        for j in context_sentence)
    
    if option in ["res","resnik"]: # lower score = more similar
        result = sorted([(v,k) for k,v in result.items()])
    else: # higher score = more similar
        result = sorted([(v,k) for k,v in result.items()],reverse=True)
    ##print result
    if best: return result[0][1];
    return result

'''
bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']
ans = max_similarity(bank_sents[0], 'bank', pos="n", option="res")
print ans
print ans[0][1].definition
'''
