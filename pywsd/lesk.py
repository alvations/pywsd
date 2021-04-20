#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

import os
from itertools import chain

import pandas as pd

from pywsd.tokenize import word_tokenize
from pywsd.cosine import cosine_similarity as cos_sim
from pywsd.stopwords import stopwords as EN_STOPWORDS
from pywsd.utils import lemmatize, porter, lemmatize_sentence, synset_properties

signatures_picklefile = os.path.dirname(os.path.abspath(__file__)) + '/data/signatures/signatures.pkl'
cached_signatures = pd.read_pickle(signatures_picklefile)

def synset_signatures_from_cache(ss: "nltk.corpus.wordnet.Synset", hyperhypo = True,
                                adapted = False, original_lesk = False):
    if original_lesk:
        signature_type = 'original'
    elif adapted:
        signature_type = 'adapted'
    else:
        signature_type = 'simple'
    return cached_signatures[ss.name()][signature_type]


def synset_signatures(ss: "wn.Synset", hyperhypo=True, adapted=False,
                      remove_stopwords=True, to_lemmatize=True, remove_numbers=True,
                      lowercase=True, original_lesk=False, from_cache=True) -> set:
    """
    Takes a Synset and returns its signature words.

    :param ss: An instance of wn.Synset.
    :return: A set of signature strings
    """
    if from_cache:
        return synset_signatures_from_cache(ss, hyperhypo, adapted, original_lesk)

    # Collects the signatures from WordNet.
    signature = []

    # Adds the definition, example sentences and lemma_names.
    signature += word_tokenize(ss.definition())

    # If the original lesk signature is requested, skip the other signatures.
    if original_lesk:
        return set(signature)

    # Adds the examples and lemma names.
    signature += chain(*[word_tokenize(eg) for eg in ss.examples()])
    signature += ss.lemma_names()

    # Includes lemma_names of hyper-/hyponyms.
    if hyperhypo:
        hyperhyponyms = set(ss.hyponyms() + ss.hypernyms() + ss.instance_hyponyms() + ss.instance_hypernyms())
        signature += set(chain(*[i.lemma_names() for i in hyperhyponyms]))

    # Includes signatures from related senses as in Adapted Lesk.
    if adapted:
        # Includes lemma_names from holonyms, meronyms and similar_tos
        related_senses = set(ss.member_holonyms() + ss.part_holonyms() + ss.substance_holonyms() + \
                             ss.member_meronyms() + ss.part_meronyms() + ss.substance_meronyms() + \
                             ss.similar_tos())
        signature += set(chain(*[i.lemma_names() for i in related_senses]))

    # Lowercase.
    signature = set(s.lower() for s in signature) if lowercase else signature

    # Removes stopwords.
    signature = set(signature).difference(EN_STOPWORDS) if remove_stopwords else signature

    # Lemmatized context is preferred over stemmed context.
    if to_lemmatize:
        signature = [lemmatize(s) if lowercase else lemmatize(s) # Lowercasing checks here.
                     for s in signature
                     # We only throw away if both remove_numbers and s is a digit are true.
                     if not (remove_numbers and s.isdigit())]

    # Keep only the unique bag-of-words
    return set(signature)


def signatures(ambiguous_word: str, pos: str = None, hyperhypo=True, adapted=False,
               remove_stopwords=True, to_lemmatize=True, remove_numbers=True,
               lowercase=True, to_stem=False, original_lesk=False, from_cache=True) -> dict:
    """
    Takes an ambiguous word and optionally its Part-Of-Speech and returns
    a dictionary where keys are the synsets and values are sets of signatures.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: dict(synset:{signatures}).
    """

    # Ensure that the POS is supported.
    pos = pos if pos in ['a', 'r', 's', 'n', 'v', None] else None

    # If the POS specified isn't found but other POS is in wordnet.
    if not wn.synsets(ambiguous_word, pos) and wn.synsets(ambiguous_word):
        pos = None

    # Holds the synset->signature dictionary.
    ss_sign = {}
    for ss in wn.synsets(ambiguous_word, pos):
        ss_sign[ss] = synset_signatures(ss, hyperhypo=hyperhypo,
                                        adapted=adapted,
                                        remove_stopwords=remove_stopwords,
                                        to_lemmatize=to_lemmatize,
                                        remove_numbers=remove_numbers,
                                        lowercase=lowercase,
                                        original_lesk=original_lesk,
                                        from_cache=from_cache)

    # Matching exact words may cause sparsity, so optional matching for stems.
    # Not advisible to use thus left out of the synsets_signatures()
    if to_stem == True:
        ss_sign = {ss:[porter.stem(s) for s in signature]
                   for ss, signature in ss_sign.items()}

    return ss_sign


def compare_overlaps_greedy(context: list, synsets_signatures: dict) -> "wn.Synset":
    """
    Calculate overlaps between the context sentence and the synset_signatures
    and returns the synset with the highest overlap.

    Note: Greedy algorithm only keeps the best sense,
    see https://en.wikipedia.org/wiki/Greedy_algorithm

    Only used by original_lesk(). Keeping greedy algorithm for documentary sake,
    because original_lesks is greedy.

    :param context: List of strings, tokenized sentence or document.
    :param synsets_signatures: dict of Synsets and the set of their corresponding signatures.
    :return: The Synset with the highest number of overlaps with its signatures.
    """

    max_overlaps = 0; lesk_sense = None
    for ss in synsets_signatures:
        overlaps = set(synsets_signatures[ss]).intersection(context)
        if len(overlaps) > max_overlaps:
            lesk_sense = ss
            max_overlaps = len(overlaps)

    return lesk_sense


def compare_overlaps(context: list, synsets_signatures: dict,
                     nbest=False, keepscore=False, normalizescore=False) -> "wn.Synset":
    """
    Calculates overlaps between the context sentence and the synset_signture
    and returns a ranked list of synsets from highest overlap to lowest.

    :param context: List of strings, tokenized sentence or document.
    :param synsets_signatures: dict of Synsets and the set of their corresponding signatures.
    :return: The Synset with the highest number of overlaps with its signatures.
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
        ranked_synsets = [i[1] for i in sorted(overlaplen_synsets, reverse=True)]

    # Returns a ranked list of synsets otherwise only the best sense.
    return ranked_synsets if nbest else ranked_synsets[0]


def original_lesk(context_sentence: str, ambiguous_word: str, dictionary=None, from_cache=True) -> "wn.Synset":
    """
    This function is the implementation of the original Lesk algorithm (1986).
    It requires a dictionary which contains the definition of the different
    sense of each word. See http://dl.acm.org/citation.cfm?id=318728

    :param context_sentence: String, sentence or document.
    :param ambiguous_word: String, a single word.
    :return: A Synset for the estimated best sense.
    """

    ambiguous_word = lemmatize(ambiguous_word)
    if not dictionary: # If dictionary is not provided, use the WN defintion.
        dictionary = signatures(ambiguous_word, original_lesk=True, from_cache=from_cache)
    best_sense = compare_overlaps_greedy(context_sentence.split(), dictionary)

    return best_sense


def simple_signatures(ambiguous_word: str, pos: str = None, lemma=True, stem=False,
                     hyperhypo=True, stop=True, from_cache=True) -> dict:
    """
    Returns a synsets_signatures dictionary that includes signature words of a
    sense from its:
    (i)   definition
    (ii)  example sentences
    (iii) hypernyms and hyponyms

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: dict(synset:{signatures})
    """
    synsets_signatures = signatures(ambiguous_word, pos=pos, hyperhypo=hyperhypo,
                            remove_stopwords=stop, to_lemmatize=lemma,
                            remove_numbers=True, lowercase=True, to_stem=stem,
                            from_cache=from_cache)
    return synsets_signatures

def simple_lesk(context_sentence: str, ambiguous_word: str,
                pos: str = None, lemma=True, stem=False, hyperhypo=True,
                stop=True, context_is_lemmatized=False,
                nbest=False, keepscore=False, normalizescore=False,
                from_cache=True) -> "wn.Synset":
    """
    Simple Lesk is somewhere in between using more than the
    original Lesk algorithm (1986) and using less signature
    words than adapted Lesk (Banerjee and Pederson, 2002)

    :param context_sentence: String, sentence or document.
    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: A Synset for the estimated best sense.
    """
    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word, pos=pos)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Get the signatures for each synset.
    ss_sign = simple_signatures(ambiguous_word, pos, lemma, stem, hyperhypo, stop,
                                from_cache=from_cache)
    # Disambiguate the sense in context.
    context_sentence = context_sentence.split() if context_is_lemmatized else lemmatize_sentence(context_sentence)
    return compare_overlaps(context_sentence, ss_sign, nbest=nbest,
                            keepscore=keepscore, normalizescore=normalizescore)


def adapted_lesk(context_sentence: str, ambiguous_word: str,
                pos: str = None, lemma=True, stem=False, hyperhypo=True,
                stop=True, context_is_lemmatized=False,
                nbest=False, keepscore=False, normalizescore=False,
                from_cache=True) -> "wn.Synset":
    """
    This function is the implementation of the Adapted Lesk algorithm,
    described in Banerjee and Pederson (2002). It makes use of the lexical
    items from semantically related senses within the wordnet
    hierarchies and to generate more lexical items for each sense.
    see www.d.umn.edu/~tpederse/Pubs/cicling2002-b.pdf‎

    :param context_sentence: String, sentence or document.
    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: A Synset for the estimated best sense.
    """

    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Get the signatures for each synset.
    ss_sign = signatures(ambiguous_word, pos=pos, hyperhypo=hyperhypo, adapted=True,
                         remove_stopwords=stop, to_lemmatize=lemma,
                         remove_numbers=True, lowercase=True, to_stem=stem,
                         from_cache=from_cache)

    # Disambiguate the sense in context.
    context_sentence = context_sentence.split() if context_is_lemmatized else lemmatize_sentence(context_sentence)
    return compare_overlaps(context_sentence, ss_sign, nbest=nbest,
                            keepscore=keepscore, normalizescore=normalizescore)


def cosine_lesk(context_sentence: str, ambiguous_word: str,
                pos: str = None, lemma=True, stem=True, hyperhypo=True,
                stop=True, context_is_lemmatized=False,
                nbest=False, from_cache=True) -> "wn.Synset":
    """
    In line with vector space models, we can use cosine to calculate overlaps
    instead of using raw overlap counts. Essentially, the idea of using
    signatures (aka 'sense paraphrases') is lesk-like.

    :param context_sentence: String, sentence or document.
    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: A Synset for the estimated best sense.
    """

    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)

    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    ss_sign = simple_signatures(ambiguous_word, pos, lemma, stem, hyperhypo, stop,
                                from_cache=from_cache)
    if context_is_lemmatized:
        context_sentence = " ".join(context_sentence.split())
    else:
        context_sentence = " ".join(lemmatize_sentence(context_sentence))

    scores = []
    for ss, signature in ss_sign.items():
        # Lowercase and replace "_" with spaces.
        signature = " ".join(map(str, signature)).lower().replace("_", " ")
        scores.append((cos_sim(context_sentence, signature), ss))

    scores = sorted(scores, reverse=True)
    return scores if nbest else scores[0][1]
