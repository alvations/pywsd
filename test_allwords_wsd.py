#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD all-words tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

import inspect
from string import punctuation

from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import brown, stopwords
from pywsd.lesk import simple_lesk
from pywsd.utils import lemmatize

"""
This is an example of how one would use pywsd for a 
all-words full text WSD.

This would involve:

Step 1: First tokenize your text such that each token is separated by whitespace
Step 2: Iterates through the tokens and only disambiguate the content words.
"""


stopwords = stopwords.words('english') + list(punctuation)

# To check default parameters of simple_lesk()
## a = inspect.getargspec(simple_lesk)
## print zip(a.args[-len(a.defaults):],a.defaults)


for sentence in brown.sents()[0:1]:
    # Step 1: Retrieves a tokenized text from brown corpus.
    sentence = " ".join(sentence).lower()
    sentence = " ".join(lemmatize(w) for w in word_tokenize(sentence))
    # Step 2: Iterates through the tokens that are content words.
    for word in sentence.split():
        if word not in stopwords:
            # Checks if content word is in 
            try:
                wn.synsets(word)[0]
                synset = simple_lesk(sentence, word, context_is_lemmatized=True)
            except:
                synset = '#NOT_IN_WN#'
        else:
            synset = '#STOPWORD/PUNCTUATION#'
        print(word, synset)
