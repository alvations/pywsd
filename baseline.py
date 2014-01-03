#!/usr/bin/env python -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import random
random.seed(0)

def random_sense(ambiguous_word):
  """ Returns a ramdom sense. """
  return random.choice(wn.synsets(ambiguous_word))

def first_sense(ambiguous_word):
  """ Returns the first sense."""
  return wn.synsets(ambiguous_word)[0]

def max_lemma_count(ambiguous_word):
  """ 
  Returns the sense with the highest lemma_name count. 
  The max_lemma_count() can be treated as a rough gauge for the 
  Most Frequent Sense (MFS), if no other sense annotated corpus is available.
  NOTE: The lemma counts are from the Brown Corpus 
  """
  sense2lemmacounts = {i:sum(j.count() for j in i.lemmas) \
                       for i in wn.synsets(ambiguous_word)}
  return max(sense2lemmacounts, key=sense2lemmacounts.get)
  