#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Corpus API tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

'''
from pywsd.semcor import SemCorpus

semcor = SemCorpus('pywsd/data/semcor3.0_naf')

for filename, sentence in semcor:
    context_sent_str = [i.text for i in sentence]
    context_sent_pos = [i.term.pos for i in sentence]
    #print sentence


######################################################################


from pywsd.semeval import SemEval2007_Coarse_WSD

coarse_wsd = SemEval2007_Coarse_WSD('pywsd/data/semeval2007_coarse_grain_wsd/')

for sentence in coarse_wsd:
    print sentence
'''


from collections import defaultdict, namedtuple
from pywsd.semcor_preprocessor import _SemCorpus

import io
import cPickle as pickle

semcor = _SemCorpus('pywsd/data/semcor3.0_naf')
Word = namedtuple('Word', 'text, sense, lemma, pos, paraid, sentid, wordid')

semcor_corpus = defaultdict(defaultdict(list))
for filename, sentence in semcor:
    filename = filename.replace('pywsd/data/semcor3.0_naf/', '')
    corpus, _, filename = filename.partition('/')
    print corpus, filename
    sent = [Word(word.text, word.term.sense, word.term.lemma, word.term.pos, 
                 word.paraid, word.sentid, word.id) for word in sentence]
    semcor_corpus[corpus][filename].append(sent)
    

with io.open('semcor-wn30.pk', 'wb') as fin:
    pickle.dump(semcor_corpus, fin)
