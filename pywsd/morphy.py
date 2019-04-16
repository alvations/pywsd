#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2018 alvations
# URL:
# For license information, see LICENSE.md

#############################################################
# Morphy: adapted from Oliver Steele's pywordnet
#############################################################

from itertools import chain, islice

from pywsd.wordnet_constants import *

def morphy(form, pos=None, check_exceptions=True):
    """
    Find a possible base form for the given form, with the given
    part of speech, by checking WordNet's list of exceptional
    forms, and by recursively stripping affixes for this part of
    speech until a form in WordNet is found.
    >>> from pywsd.morphy import morphy
    >>> print(morphy('dogs'))
    dog
    >>> print(morphy('churches'))
    church
    >>> print(morphy('aardwolves'))
    aardwolf
    >>> print(morphy('abaci'))
    abacus
    >>> morphy('hardrock', ADV)
    >>> print(morphy('book', NOUN))
    book
    >>> morphy('book', wn.ADJ)
    """

    if pos is None:
        morphy = _morphy
        analyses = chain(a for p in POS_LIST for a in morphy(form, p))
    else:
        analyses = _morphy(form, pos, check_exceptions)

    # get the first one we find
    first = list(islice(analyses, 1))
    if len(first) == 1:
        return first[0]
    else:
        return None


def _morphy(form, pos, check_exceptions=True):
    # from jordanbg:
    # Given an original string x
    # 1. Apply rules once to the input to get y1, y2, y3, etc.
    # 2. Return all that are in the database
    # 3. If there are no matches, keep applying rules until you either
    #    find a match or you can't go any further

    exceptions = exception_map[pos]
    substitutions = MORPHOLOGICAL_SUBSTITUTIONS[pos]

    def apply_rules(forms):
        return [
            form[: -len(old)] + new
            for form in forms
            for old, new in substitutions
            if form.endswith(old)
        ]

    def filter_forms(forms):
        result = []
        seen = set()
        for form in forms:
            if form in lemma_pos_offset_map:
                if pos in lemma_pos_offset_map[form]:
                    if form not in seen:
                        result.append(form)
                        seen.add(form)
        return result

    # 0. Check the exception lists
    if check_exceptions:
        if form in exceptions:
            return filter_forms([form] + exceptions[form])

    # 1. Apply rules once to the input to get y1, y2, y3, etc.
    forms = apply_rules([form])

    # 2. Return all that are in the database (and check the original too)
    results = filter_forms([form] + forms)
    if results:
        return results

    # 3. If there are no matches, keep applying rules until we find a match
    while forms:
        forms = apply_rules(forms)
        results = filter_forms(forms)
        if results:
            return results

    # Return an empty list if we can't find anything
    return []
