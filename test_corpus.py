#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Corpus API tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

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