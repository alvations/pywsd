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
    print disambiguate(sentence, simple_lesk, prefersNone=True, keepLemmas=True)
    print disambiguate(sentence, original_lesk)
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

 
''' 
# TODO: do proper doctests...

# Lemma options and None when no Synset.
>>> disambiguate('I went to the bank to deposit my money')
[('I', '#STOPWORD/PUNCTUATION#'), ('went', Synset('go.v.28')), ('to', '#STOPWORD/PUNCTUATION#'), ('the', '#STOPWORD/PUNCTUATION#'), ('bank', Synset('depository_financial_institution.n.01')), ('to', '#STOPWORD/PUNCTUATION#'), ('deposit', Synset('deposit.n.04')), ('my', '#STOPWORD/PUNCTUATION#'), ('money', Synset('money.n.03'))]
>>> disambiguate('I went to the bank to deposit my money', prefersNone=True, keepLemmas=True)
[('I', 'i', None), ('went', 'went', Synset('go.v.28')), ('to', 'to', None), ('the', 'the', None), ('bank', 'bank', Synset('depository_financial_institution.n.01')), ('to', 'to', None), ('deposit', 'deposit', Synset('deposit.n.04')), ('my', 'my', None), ('money', 'money', Synset('money.n.03'))]
# Using alternative algorithms.
>>> disambiguate('I went to the bank to deposit my money', algorithm=cosine_lesk, prefersNone=True)
[('I', None), ('went', Synset('travel.v.01')), ('to', None), ('the', None), ('bank', Synset('bank.v.05')), ('to', None), ('deposit', Synset('down_payment.n.01')), ('my', None), ('money', Synset('money.n.01'))]
>>> disambiguate('I went to the bank to deposit my money', algorithm=maxsim, similarity_option='wup', prefersNone=True)
[('I', None), ('went', Synset('sound.v.02')), ('to', None), ('the', None), ('bank', Synset('deposit.v.02')), ('to', None), ('deposit', Synset('deposit.v.02')), ('my', None), ('money', Synset('money.n.01'))]
'''
 