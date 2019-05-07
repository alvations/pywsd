#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): all-words WSD
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

from string import punctuation

from nltk import pos_tag

from pywsd.lesk import simple_lesk, original_lesk
from pywsd.similarity import max_similarity
from pywsd.stopwords import stopwords
from pywsd.tokenize import word_tokenize
from pywsd.utils import lemmatize, lemmatize_sentence

"""
This is a module for all-words full text WSD

This would involve:
Step 1: First tokenize your text such that each token is separated by whitespace
Step 2: Iterates through the tokens and only disambiguate the content words.
"""

def disambiguate(sentence, algorithm=simple_lesk,
                 context_is_lemmatized=False, similarity_option='path',
                 keepLemmas=False, prefersNone=True, from_cache=True,
                 tokenizer=word_tokenize):

    tagged_sentence = []
    # Pre-lemmatize the sentnece before WSD
    if not context_is_lemmatized:
        surface_words, lemmas, morphy_poss = lemmatize_sentence(sentence, keepWordPOS=True, tokenizer=tokenizer)
        lemma_sentence = " ".join(lemmas)
    else:
        lemma_sentence = sentence # TODO: Miss out on POS specification, how to resolve?
    for word, lemma, pos in zip(surface_words, lemmas, morphy_poss):
        if lemma not in stopwords: # Checks if it is a content word
            if wn.synsets(lemma):
                if algorithm == original_lesk: # Note: Original doesn't care about lemmas
                    synset = algorithm(lemma_sentence, lemma, from_cache=from_cache)
                elif algorithm == max_similarity:
                    synset = algorithm(lemma_sentence, lemma, pos=pos, option=similarity_option)
                else:
                    synset = algorithm(lemma_sentence, lemma, pos=pos, context_is_lemmatized=True,
                                       from_cache=from_cache)
            else: # In case the content word is not in WordNet.
                synset = '#NOT_IN_WN#'
        else:
            synset = '#STOPWORD/PUNCTUATION#'
        if keepLemmas:
            tagged_sentence.append((word, lemma, synset))
        else:
            tagged_sentence.append((word, synset))
    # Change #NOT_IN_WN# and #STOPWORD/PUNCTUATION# into None.
    if prefersNone and not keepLemmas:
        tagged_sentence = [(word, None) if str(tag).startswith('#')
                           else (word, tag) for word, tag in tagged_sentence]
    if prefersNone and keepLemmas:
        tagged_sentence = [(word, lemma, None) if str(tag).startswith('#')
                           else (word, lemma, tag) for word, lemma, tag in tagged_sentence]
    return tagged_sentence
