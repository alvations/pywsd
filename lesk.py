#!/usr/bin/env python -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from itertools import chain

porter = PorterStemmer()

def simple_lesk(context_sentence, ambiguous_word, \
                pos=None, stem=True, hyperhypo=True):
  max_overlaps = 0; lesk_sense = None
  context_sentence = context_sentence.split()
  
  for ss in wn.synsets(ambiguous_word):
    # If POS is specified.
    if pos and ss.pos is not pos:
      continue
    
    lesk_dictionary = []
    # Includes definition.
    lesk_dictionary+= ss.definition.split()
    # Includes lemma_names.
    lesk_dictionary+= ss.lemma_names

    # Optional: includes lemma_names of hypernyms and hyponyms.
    if hyperhypo == True:
      lesk_dictionary+= list(chain(*[i.lemma_names for i \
                                     in ss.hypernyms()+ss.hyponyms()]))    
    
    # Matching exact words causes sparsity, so optional matching for stems.
    if stem == True: 
      lesk_dictionary = [porter.stem(i) for i in lesk_dictionary]
      context_sentence = [porter.stem(i) for i in context_sentence] 
    
    overlaps = set(lesk_dictionary).intersection(context_sentence)
    
    if len(overlaps) > max_overlaps:
      lesk_sense = ss
      max_overlaps = len(overlaps)
  return lesk_sense