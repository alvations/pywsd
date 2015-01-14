#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD all-words tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

from string import punctuation

from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import brown, stopwords


from pywsd.lesk import simple_lesk, original_lesk, cosine_lesk, adapted_lesk
from pywsd.similarity import max_similarity
from pywsd.utils import lemmatize
from pywsd.allwords_wsd import disambiguate

print "======== TESTING all-words lesk ===========\n"
for sentence in brown.sents()[:10]:
    # Retrieves a tokenized text from brown corpus.
    sentence = " ".join(sentence)
    # Annotate the full sentence.
    print disambiguate(sentence, original_lesk)
    print disambiguate(sentence, simple_lesk, prefersNone=True, keepLemmas=True)
    print disambiguate(sentence, adapted_lesk, keepLemmas=True)
    print disambiguate(sentence, cosine_lesk, prefersNone=True)
    print
print

print "======== TESTING all-words path maxsim ===========\n"
print "This is going to take some time, have some coffee...\n"
for sentence in brown.sents()[0:1]:
    # Retrieves a tokenized text from brown corpus.
    sentence = " ".join(sentence)
    # Annotate the full sentence.
    print disambiguate(sentence, max_similarity, similarity_option='path')
    print disambiguate(sentence, max_similarity, similarity_option='wup')
print

print "======== TESTING all-words info content maxsim ==========="
print "===This is going to take some time, have some coffee...===\n"
for sentence in brown.sents()[0:1]:
    # Retrieves a tokenized text from brown corpus.
    sentence = " ".join(sentence)
    # Annotate the full sentence.
    print disambiguate(sentence, max_similarity, similarity_option='lch')
    print disambiguate(sentence, max_similarity, similarity_option='res')
    print disambiguate(sentence, max_similarity, similarity_option='jcn')
    print disambiguate(sentence, max_similarity, similarity_option='lin')
 