#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

from functools import lru_cache
from itertools import chain

from pywsd._wordnet import wn
from pywsd.tokenize import word_tokenize
from pywsd.cosine import cosine_similarity as cos_sim
from pywsd.stopwords import stopwords as EN_STOPWORDS
from pywsd.utils import lemmatize, porter, lemmatize_sentence


def _signature_tokens(ss, hyperhypo: bool, adapted: bool,
                      remove_stopwords: bool, to_lemmatize: bool,
                      remove_numbers: bool, lowercase: bool,
                      original_lesk: bool) -> frozenset:
    """Raw signature computation for a synset. Cached by synset id + options."""
    signature = list(word_tokenize(ss.definition() or ""))

    if original_lesk:
        return frozenset(signature)

    signature += chain(*[word_tokenize(eg) for eg in ss.examples()])
    signature += ss.lemmas()

    if hyperhypo:
        neighbours = set(ss.hyponyms() + ss.hypernyms())
        neighbours |= set(ss.get_related("instance_hypernym"))
        neighbours |= set(ss.get_related("instance_hyponym"))
        signature += chain(*[n.lemmas() for n in neighbours])

    if adapted:
        related = set(ss.holonyms() + ss.meronyms() + ss.get_related("similar"))
        signature += chain(*[n.lemmas() for n in related])

    if lowercase:
        signature = [s.lower() for s in signature]

    if remove_stopwords:
        signature = [s for s in signature if s not in EN_STOPWORDS]

    if to_lemmatize:
        signature = [lemmatize(s) for s in signature
                     if not (remove_numbers and s.isdigit())]

    return frozenset(signature)


@lru_cache(maxsize=None)
def _cached_signature(synset_id: str, hyperhypo: bool, adapted: bool,
                      remove_stopwords: bool, to_lemmatize: bool,
                      remove_numbers: bool, lowercase: bool,
                      original_lesk: bool) -> frozenset:
    ss = wn.synset(synset_id)
    return _signature_tokens(ss, hyperhypo, adapted, remove_stopwords,
                             to_lemmatize, remove_numbers, lowercase,
                             original_lesk)


def synset_signatures(ss, hyperhypo=True, adapted=False,
                      remove_stopwords=True, to_lemmatize=True,
                      remove_numbers=True, lowercase=True,
                      original_lesk=False, from_cache=True) -> set:
    """
    Takes a Synset and returns its signature words.

    :param ss: A ``wn.Synset``.
    :return: A set of signature strings.

    The ``from_cache`` parameter is retained for backward compatibility but is
    now a no-op; results are memoized in-process regardless.
    """
    tokens = _cached_signature(ss.id, hyperhypo, adapted, remove_stopwords,
                               to_lemmatize, remove_numbers, lowercase,
                               original_lesk)
    return set(tokens)


def signatures(ambiguous_word: str, pos: str = None, hyperhypo=True, adapted=False,
               remove_stopwords=True, to_lemmatize=True, remove_numbers=True,
               lowercase=True, to_stem=False, original_lesk=False,
               from_cache=True) -> dict:
    """
    Takes an ambiguous word and optionally its Part-Of-Speech and returns
    a dictionary where keys are the synsets and values are sets of signatures.

    :param ambiguous_word: String, a single word.
    :param pos: String, one of 'a', 'r', 's', 'n', 'v', or None.
    :return: dict(synset:{signatures}).
    """
    pos = pos if pos in ['a', 'r', 's', 'n', 'v', None] else None

    if not wn.synsets(ambiguous_word, pos) and wn.synsets(ambiguous_word):
        pos = None

    ss_sign = {}
    for ss in wn.synsets(ambiguous_word, pos):
        ss_sign[ss] = synset_signatures(
            ss, hyperhypo=hyperhypo, adapted=adapted,
            remove_stopwords=remove_stopwords, to_lemmatize=to_lemmatize,
            remove_numbers=remove_numbers, lowercase=lowercase,
            original_lesk=original_lesk,
        )

    if to_stem:
        ss_sign = {ss: {porter.stem(s) for s in sig}
                   for ss, sig in ss_sign.items()}

    return ss_sign


def compare_overlaps_greedy(context: list, synsets_signatures: dict):
    """
    Calculate overlaps between the context sentence and the synset_signatures
    and returns the synset with the highest overlap.

    Greedy: keeps the first best sense, used by ``original_lesk``.
    """
    max_overlaps = 0
    lesk_sense = None
    for ss, sig in synsets_signatures.items():
        overlaps = set(sig).intersection(context)
        if len(overlaps) > max_overlaps:
            lesk_sense = ss
            max_overlaps = len(overlaps)
    return lesk_sense


def compare_overlaps(context: list, synsets_signatures: dict,
                     nbest=False, keepscore=False, normalizescore=False):
    """
    Calculates overlaps between the context and each synset signature,
    returning a ranked list (or the best synset).
    """
    overlaplen_synsets = [(len(set(sig).intersection(context)), ss)
                          for ss, sig in synsets_signatures.items()]
    ranked_synsets = sorted(overlaplen_synsets, key=lambda x: x[0], reverse=True)

    if normalizescore:
        total = float(sum(i[0] for i in ranked_synsets)) or 1.0
        ranked_synsets = [(count / total, ss) for count, ss in ranked_synsets]

    if not keepscore:
        ranked_synsets = [ss for _, ss in ranked_synsets]

    return ranked_synsets if nbest else ranked_synsets[0]


def original_lesk(context_sentence: str, ambiguous_word: str,
                  dictionary=None, from_cache=True):
    """Lesk (1986) — overlap against WordNet definitions only."""
    ambiguous_word = lemmatize(ambiguous_word)
    if not dictionary:
        dictionary = signatures(ambiguous_word, original_lesk=True)
    return compare_overlaps_greedy(context_sentence.split(), dictionary)


def simple_signatures(ambiguous_word: str, pos: str = None, lemma=True, stem=False,
                      hyperhypo=True, stop=True, from_cache=True) -> dict:
    """Signatures from definition + examples + hyper/hyponyms."""
    return signatures(
        ambiguous_word, pos=pos, hyperhypo=hyperhypo,
        remove_stopwords=stop, to_lemmatize=lemma,
        remove_numbers=True, lowercase=True, to_stem=stem,
    )


def simple_lesk(context_sentence: str, ambiguous_word: str,
                pos: str = None, lemma=True, stem=False, hyperhypo=True,
                stop=True, context_is_lemmatized=False,
                nbest=False, keepscore=False, normalizescore=False,
                from_cache=True):
    """
    Simple Lesk — between the original (1986) and adapted Lesk (Banerjee &
    Pederson, 2002).
    """
    ambiguous_word = lemmatize(ambiguous_word, pos=pos)
    if not wn.synsets(ambiguous_word):
        return None
    ss_sign = simple_signatures(ambiguous_word, pos, lemma, stem, hyperhypo, stop)
    context_sentence = (context_sentence.split() if context_is_lemmatized
                        else lemmatize_sentence(context_sentence))
    return compare_overlaps(context_sentence, ss_sign, nbest=nbest,
                            keepscore=keepscore, normalizescore=normalizescore)


def adapted_lesk(context_sentence: str, ambiguous_word: str,
                 pos: str = None, lemma=True, stem=False, hyperhypo=True,
                 stop=True, context_is_lemmatized=False,
                 nbest=False, keepscore=False, normalizescore=False,
                 from_cache=True):
    """Adapted Lesk (Banerjee & Pederson, 2002) — extends simple Lesk with
    holonyms, meronyms, and similar-to relations."""
    ambiguous_word = lemmatize(ambiguous_word)
    if not wn.synsets(ambiguous_word):
        return None
    ss_sign = signatures(
        ambiguous_word, pos=pos, hyperhypo=hyperhypo, adapted=True,
        remove_stopwords=stop, to_lemmatize=lemma,
        remove_numbers=True, lowercase=True, to_stem=stem,
    )
    context_sentence = (context_sentence.split() if context_is_lemmatized
                        else lemmatize_sentence(context_sentence))
    return compare_overlaps(context_sentence, ss_sign, nbest=nbest,
                            keepscore=keepscore, normalizescore=normalizescore)


def cosine_lesk(context_sentence: str, ambiguous_word: str,
                pos: str = None, lemma=True, stem=True, hyperhypo=True,
                stop=True, context_is_lemmatized=False,
                nbest=False, from_cache=True):
    """Cosine-similarity Lesk — vector-space overlap of signature and context."""
    ambiguous_word = lemmatize(ambiguous_word)
    if not wn.synsets(ambiguous_word):
        return None
    ss_sign = simple_signatures(ambiguous_word, pos, lemma, stem, hyperhypo, stop)
    context_sentence = (" ".join(context_sentence.split()) if context_is_lemmatized
                        else " ".join(lemmatize_sentence(context_sentence)))
    scores = []
    for ss, signature in ss_sign.items():
        sig_text = " ".join(map(str, signature)).lower().replace("_", " ")
        scores.append((cos_sim(context_sentence, sig_text), ss))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores if nbest else scores[0][1]
