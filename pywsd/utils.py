# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Python Word Sense Disambiguation (pyWSD): Misc utility functions
# Copyright (C) 2014-2020 alvations
# For license information, see LICENSE.md

import re
from functools import reduce

from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag

from pywsd._wordnet import wn
from pywsd.tokenize import word_tokenize


def remove_tags(text: str) -> str:
    """Remove <tags> in angled brackets from text."""
    tags = {i: " " for i in re.findall(r"(<[^>\n]*>)", text.strip())}
    no_tag_text = reduce(lambda x, kv: x.replace(*kv), tags.items(), text)
    return " ".join(no_tag_text.split())


def semcor_to_synset(sensekey: str):
    """Look up a synset given a SemCor sensekey (e.g. ``live%2:42:06::``)."""
    return wn.lemma_from_key(sensekey).synset()


porter = PorterStemmer()
wnl = WordNetLemmatizer()


def lemmatize(ambiguous_word: str, pos: str = None, neverstem=False,
              lemmatizer=wnl, stemmer=porter) -> str:
    """
    Try to convert a surface word into a lemma; if the lemmatized form is not
    in WordNet, fall back to the stem. Returns the surface word if neither is
    found (or if ``neverstem`` is set and lemma fails).
    """
    pos = pos if pos else penn2morphy(pos_tag([ambiguous_word])[0][1],
                                      default_to_noun=True)
    lemma = lemmatizer.lemmatize(ambiguous_word, pos=pos)
    if wn.synsets(lemma):
        return lemma
    if neverstem:
        return ambiguous_word
    stem = stemmer.stem(ambiguous_word)
    return stem if wn.synsets(stem) else ambiguous_word


def penn2morphy(penntag, returnNone=False, default_to_noun=False) -> str:
    """Convert a Penn Treebank tag to a Morphy POS code."""
    morphy_tag = {'NN': 'n', 'JJ': 'a', 'VB': 'v', 'RB': 'r'}
    try:
        return morphy_tag[penntag[:2]]
    except KeyError:
        if returnNone:
            return None
        if default_to_noun:
            return 'n'
        return ''


def lemmatize_sentence(sentence: str, neverstem=False, keepWordPOS=False,
                       tokenizer=word_tokenize, postagger=pos_tag,
                       lemmatizer=wnl, stemmer=porter):
    words, lemmas, poss = [], [], []
    for word, pos in postagger(tokenizer(sentence)):
        morphy_pos = penn2morphy(pos)
        lemmas.append(lemmatize(word.lower(), morphy_pos, neverstem,
                                lemmatizer, stemmer))
        poss.append(morphy_pos)
        words.append(word)

    if keepWordPOS:
        return words, lemmas, [None if i == '' else i for i in poss]
    return lemmas


def has_synset(word: str) -> list:
    """Return the list of synsets of a word after lemmatization."""
    return wn.synsets(lemmatize(word, neverstem=True))
