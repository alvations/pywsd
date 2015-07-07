#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

import string
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag

from cosine import cosine_similarity as cos_sim
from utils import lemmatize, porter, lemmatize_sentence, synset_properties

EN_STOPWORDS = stopwords.words('english')

def compare_overlaps_greedy(context, synsets_signatures):
    """
    Calculate overlaps between the context sentence and the synset_signature
    and returns the synset with the highest overlap.
    
    Note: Greedy algorithm only keeps the best sense, 
    see https://en.wikipedia.org/wiki/Greedy_algorithm
    
    Only used by original_lesk(). Keeping greedy algorithm for documentary sake, 
    because original_lesks is greedy.
    """
    max_overlaps = 0; lesk_sense = None
    for ss in synsets_signatures:
        overlaps = set(synsets_signatures[ss]).intersection(context)
        if len(overlaps) > max_overlaps:
            lesk_sense = ss
            max_overlaps = len(overlaps)    
    return lesk_sense

def compare_overlaps(context, synsets_signatures, \
                     nbest=False, keepscore=False, normalizescore=False):
    """ 
    Calculates overlaps between the context sentence and the synset_signture
    and returns a ranked list of synsets from highest overlap to lowest.
    """
    overlaplen_synsets = [] # a tuple of (len(overlap), synset).
    for ss in synsets_signatures:
        overlaps = set(synsets_signatures[ss]).intersection(context)
        overlaplen_synsets.append((len(overlaps), ss))
    
    # Rank synsets from highest to lowest overlap.
    ranked_synsets = sorted(overlaplen_synsets, reverse=True)
    
    # Normalize scores such that it's between 0 to 1. 
    if normalizescore:
        total = float(sum(i[0] for i in ranked_synsets))
        ranked_synsets = [(i/total,j) for i,j in ranked_synsets]
      
    if not keepscore: # Returns a list of ranked synsets without scores
        ranked_synsets = [i[1] for i in sorted(overlaplen_synsets, \
                                               reverse=True)]
      
    if nbest: # Returns a ranked list of synsets.
        return ranked_synsets
    else: # Returns only the best sense.
        return ranked_synsets[0]

def original_lesk(context_sentence, ambiguous_word, dictionary=None):
    """
    This function is the implementation of the original Lesk algorithm (1986).
    It requires a dictionary which contains the definition of the different
    sense of each word. See http://dl.acm.org/citation.cfm?id=318728
    """
    ambiguous_word = lemmatize(ambiguous_word)
    if not dictionary: # If dictionary is not provided, use the WN defintion.
        dictionary = {}
        for ss in wn.synsets(ambiguous_word):
            ss_definition = synset_properties(ss, 'definition')
            dictionary[ss] = ss_definition
    best_sense = compare_overlaps_greedy(context_sentence.split(), dictionary)
    return best_sense    

def simple_signature(ambiguous_word, pos=None, lemma=True, stem=False, \
                     hyperhypo=True, stop=True):
    """ 
    Returns a synsets_signatures dictionary that includes signature words of a 
    sense from its:
    (i)   definition
    (ii)  example sentences
    (iii) hypernyms and hyponyms
    """
    synsets_signatures = {}
    for ss in wn.synsets(ambiguous_word):
        try: # If POS is specified.
            if pos and str(ss.pos()) != pos:
                continue
        except:
            if pos and str(ss.pos) != pos:
                continue
        signature = []
        # Includes definition.
        ss_definition = synset_properties(ss, 'definition')
        signature+=ss_definition
        # Includes examples
        ss_examples = synset_properties(ss, 'examples')
        signature+=list(chain(*[i.split() for i in ss_examples]))
        # Includes lemma_names.
        ss_lemma_names = synset_properties(ss, 'lemma_names')
        signature+= ss_lemma_names
        
        # Optional: includes lemma_names of hypernyms and hyponyms.
        if hyperhypo == True:
            ss_hyponyms = synset_properties(ss, 'hyponyms')
            ss_hypernyms = synset_properties(ss, 'hypernyms')
            ss_hypohypernyms = ss_hypernyms+ss_hyponyms
            signature+= list(chain(*[i.lemma_names() for i in ss_hypohypernyms]))
        
        # Optional: removes stopwords.
        if stop == True: 
            signature = [i for i in signature if i not in EN_STOPWORDS]
        # Lemmatized context is preferred over stemmed context.
        if lemma == True: 
            signature = [lemmatize(i) for i in signature]
        # Matching exact words may cause sparsity, so optional matching for stems.
        if stem == True: 
            signature = [porter.stem(i) for i in signature]
        synsets_signatures[ss] = signature
        
    return synsets_signatures

def simple_lesk(context_sentence, ambiguous_word, \
                pos=None, lemma=True, stem=False, hyperhypo=True, \
                stop=True, context_is_lemmatized=False, \
                nbest=False, keepscore=False, normalizescore=False):
    """
    Simple Lesk is somewhere in between using more than the 
    original Lesk algorithm (1986) and using less signature 
    words than adapted Lesk (Banerjee and Pederson, 2002)
    """
    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word) 
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Get the signatures for each synset.
    ss_sign = simple_signature(ambiguous_word, pos, lemma, stem, hyperhypo)
    # Disambiguate the sense in context.
    if context_is_lemmatized:
        context_sentence = context_sentence.split()
    else:
        context_sentence = lemmatize_sentence(context_sentence)
    best_sense = compare_overlaps(context_sentence, ss_sign, \
                                    nbest=nbest, keepscore=keepscore, \
                                    normalizescore=normalizescore)  
    return best_sense

def adapted_lesk(context_sentence, ambiguous_word, \
                pos=None, lemma=True, stem=True, hyperhypo=True, \
                stop=True, context_is_lemmatized=False, \
                nbest=False, keepscore=False, normalizescore=False):
    """
    This function is the implementation of the Adapted Lesk algorithm, 
    described in Banerjee and Pederson (2002). It makes use of the lexical 
    items from semantically related senses within the wordnet 
    hierarchies and to generate more lexical items for each sense. 
    see www.d.umn.edu/~tpederse/Pubs/cicling2002-b.pdf‎
    """
    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Get the signatures for each synset.
    ss_sign = simple_signature(ambiguous_word, pos, lemma, stem, hyperhypo)
    for ss in ss_sign:
        # Includes holonyms.
        ss_mem_holonyms = synset_properties(ss, 'member_holonyms')
        ss_part_holonyms = synset_properties(ss, 'part_holonyms')
        ss_sub_holonyms = synset_properties(ss, 'substance_holonyms')
        # Includes meronyms.
        ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
        ss_part_meronyms = synset_properties(ss, 'part_meronyms')
        ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')
        # Includes similar_tos
        ss_simto = synset_properties(ss, 'similar_tos')
        
        related_senses = list(set(ss_mem_holonyms+ss_part_holonyms+ 
                                  ss_sub_holonyms+ss_mem_meronyms+ 
                                  ss_part_meronyms+ss_sub_meronyms+ ss_simto))
    
        signature = list([j for j in chain(*[synset_properties(i, 'lemma_names') 
                                             for i in related_senses]) 
                          if j not in EN_STOPWORDS])
        
    # Lemmatized context is preferred over stemmed context
    if lemma == True:
        signature = [lemmatize(i) for i in signature]
    # Matching exact words causes sparsity, so optional matching for stems.
    if stem == True:
        signature = [porter.stem(i) for i in signature]
    # Adds the extended signature to the simple signatures.
    ss_sign[ss]+=signature
  
    # Disambiguate the sense in context.
    if context_is_lemmatized:
        context_sentence = context_sentence.split()
    else:
        context_sentence = lemmatize_sentence(context_sentence)
    best_sense = compare_overlaps(context_sentence, ss_sign, \
                                    nbest=nbest, keepscore=keepscore, \
                                    normalizescore=normalizescore)
    return best_sense

def cosine_lesk(context_sentence, ambiguous_word, \
                pos=None, lemma=True, stem=True, hyperhypo=True, \
                stop=True, context_is_lemmatized=False, \
                nbest=False):
    """ 
    In line with vector space models, we can use cosine to calculate overlaps
    instead of using raw overlap counts. Essentially, the idea of using 
    signatures (aka 'sense paraphrases') is lesk-like.
    """
    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    synsets_signatures = simple_signature(ambiguous_word, pos, lemma, stem, hyperhypo)
    
    if context_is_lemmatized:
        context_sentence = " ".join(context_sentence.split())
    else:
        context_sentence = " ".join(lemmatize_sentence(context_sentence))
    
    scores = []
    for ss, signature in synsets_signatures.items():
        # Lowercase and replace "_" with spaces.
        signature = " ".join(map(str, signature)).lower().replace("_", " ")
        # Removes punctuation.
        signature = [i for i in word_tokenize(signature) \
                     if i not in string.punctuation]
        # Optional: remove stopwords.
        if stop:
            signature = [i for i in signature if i not in EN_STOPWORDS]
        # Optional: Lemmatize the tokens.
        if lemma == True:
            signature = [lemmatize(i) for i in signature]
        # Optional: stem the tokens.
        if stem:
            signature = [porter.stem(i) for i in signature]
        scores.append((cos_sim(context_sentence, " ".join(signature)), ss))
        
        if not nbest:
            return sorted(scores, reverse=True)[0][1]
        else:
            return [(j,i) for i,j in sorted(scores, reverse=True)]

