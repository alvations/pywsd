#!/usr/bin/env python -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from itertools import chain

porter = PorterStemmer()

def compare_overlaps(context, synset_signature):
  max_overlaps = 0; lesk_sense = None
  for ss in synset_signature:
    overlaps = set(synset_signature[ss]).intersection(context)
    if len(overlaps) > max_overlaps:
      lesk_sense = ss
      max_overlaps = len(overlaps)    
  return lesk_sense

def original_lesk (context_sentence, ambiguous_word, dictionary=None):
  """
  This function is the implementation of the original Lesk algorithm (1986).
  It requires a dictionary which contains the definition of the different
  sense of each word. See http://goo.gl/8TB15w
  """
  if not dictionary:
    dictionary = {ss:ss.definition.split() for ss in wn.synsets(ambiguous_word)}
  best_sense = compare_overlaps(context_sentence.split(), dictionary)
  return best_sense    

def simple_signature(ambiguous_word, pos=None, stem=True, hyperhypo=True):
  """ 
  Returns a synset_signature dictionary that includes signature words of a 
  sense from its:
  (i)   definition
  (ii)  example sentences
  (iii) hypernyms and hyponyms
  """
  synset_signature = {}
  for ss in wn.synsets(ambiguous_word):
    # If POS is specified.
    if pos and ss.pos is not pos:
      continue
    signature = []
    # Includes definition.
    signature+= ss.definition.split()
    # Includes examples
    signature+= list(chain(*[i.split() for i in ss.examples]))
    # Includes lemma_names.
    signature+= ss.lemma_names
    # Optional: includes lemma_names of hypernyms and hyponyms.
    if hyperhypo == True:
      signature+= list(chain(*[i.lemma_names for i \
                               in ss.hypernyms()+ss.hyponyms()]))    
    # Matching exact words causes sparsity, so optional matching for stems.
    if stem == True: 
      signature = [porter.stem(i) for i in signature]
    synset_signature[ss] = signature
  return synset_signature

def simple_lesk(context_sentence, ambiguous_word, \
                pos=None, stem=True, hyperhypo=True):
  """
  Simple Lesk is somewhere in between using more than the 
  original Lesk algorithm (1986) and using less signature 
  words than adapted Lesk (Banerjee and Pederson, 2002)
  """
  # Get the signatures for each synset.
  ss_sign = simple_signature(ambiguous_word, pos, stem, hyperhypo)
  # Disambiguate the sense in context.
  context_sentence = [porter.stem(i) for i in context_sentence.split()]
  best_sense = compare_overlaps(context_sentence, ss_sign)  
  return best_sense

def adapted_lesk(context_sentence, ambiguous_word, \
                pos=None, stem=True, hyperhypo=True):
  """
  This function is the implementation of the Adapted Lesk algorithm, 
  described in Banerjee and Pederson (2002). It makes use of the lexical 
  items from semantically related senses within the wordnet 
  hierarchies and to generate more lexical items for each sense. 
  see www.d.umn.edu/~tpederse/Pubs/cicling2002-b.pdf‎
  """
  # Get the signatures for each synset.
  ss_sign = simple_signature(ambiguous_word, pos, stem, hyperhypo)
  for ss in ss_sign:
    related_senses = list(set(ss.member_holonyms() + ss.member_meronyms() + 
                             ss.part_meronyms() + ss.part_holonyms() + 
                             ss.similar_tos() + ss.substance_holonyms() + 
                             ss.substance_meronyms()))
    signature = list(chain(*[i.lemma_names for i in related_senses]))
    # Matching exact words causes sparsity, so optional matching for stems.
    if stem == True: 
      signature = [porter.stem(i) for i in signature]
    ss_sign[ss]+=signature
  
  # Disambiguate the sense in context.
  context_sentence = [porter.stem(i) for i in context_sentence.split()]
  best_sense = compare_overlaps(context_sentence, ss_sign)
  return best_sense

