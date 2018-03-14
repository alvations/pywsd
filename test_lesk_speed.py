#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD all-words lesk speed tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

from __future__ import print_function

import time
from nltk.corpus import brown

from pywsd.lesk import simple_lesk, original_lesk, cosine_lesk, adapted_lesk
from pywsd.allwords_wsd import disambiguate

print("======== TESTING all-words lesk (`from_cache=True`)===========")
start = time.time()
for sentence in brown.sents()[:10]:
    sentence = " ".join(sentence)
    disambiguate(sentence, simple_lesk, prefersNone=True, keepLemmas=True)
    disambiguate(sentence, original_lesk)
    disambiguate(sentence, adapted_lesk, keepLemmas=True)
print('Disambiguating 100 brown sentences took {} secs'.format(time.time() - start))


print("======== TESTING all-words lesk (`from_cache=False`)===========")
start = time.time()
for sentence in brown.sents()[:10]:
    sentence = " ".join(sentence)
    disambiguate(sentence, simple_lesk, prefersNone=True, keepLemmas=True, from_cache=False)
    disambiguate(sentence, original_lesk, from_cache=False)
    disambiguate(sentence, adapted_lesk, keepLemmas=True, from_cache=False)
print('Disambiguating 10 brown sentences took {} secs'.format(time.time() - start))
