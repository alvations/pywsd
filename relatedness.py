#!/usr/bin/env python -*- coding: utf-8 -*-

"""
User requested feature, still work in progress...
"""

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize

def max_wupa(context_sentence, ambiguous_word):
  """ 
  WSD by Maximizing Wu-Palmer Similarity.
  
  Perform WSD by maximizing the sum of maximum Wu-Palmer score between possible 
  synsets of all words in the context sentence and the possible synsets of the 
  ambiguous words (see http://goo.gl/XMq2BI):
  {argmax}_{synset(a)}(\sum_{i}^{n}{{max}_{synset(i)}(Wu-Palmer(i,a))}
  
  Wu-Palmer (1994) similarity is based on path length; the similarity between 
  two synsets accounts for the number of nodes along the shortest path between 
  them. (see http://acl.ldc.upenn.edu/P/P94/P94-1019.pdf)
  """
  
  result = {}
  for i in wn.synsets(ambiguous_word):
    result[i] = sum(max([i.wup_similarity(k) for k in wn.synsets(j)]+[0]) \
                    for j in word_tokenize(context_sentence))
  result = sorted([(v,k) for k,v in result.items()],reverse=True)
  return result
  
bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']
ans = max_wupa(bank_sents[0], 'bank')
print ans
print ans[0][1].definition