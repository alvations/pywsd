#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Tokenizer
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

import re

from nltk import sent_tokenize

class MacIntyreContractions:
    """
    List of contractions adapted from Robert MacIntyre's tokenizer.
    """

    CONTRACTIONS2 = [
        r"(?i)\b(can)(?#X)(not)\b",
        r"(?i)\b(d)(?#X)('ye)\b",
        r"(?i)\b(gim)(?#X)(me)\b",
        r"(?i)\b(gon)(?#X)(na)\b",
        r"(?i)\b(got)(?#X)(ta)\b",
        r"(?i)\b(lem)(?#X)(me)\b",
        r"(?i)\b(mor)(?#X)('n)\b",
        r"(?i)\b(wan)(?#X)(na)\s",
    ]
    CONTRACTIONS3 = [r"(?i) ('t)(?#X)(is)\b", r"(?i) ('t)(?#X)(was)\b"]
    CONTRACTIONS4 = [r"(?i)\b(whad)(dd)(ya)\b", r"(?i)\b(wha)(t)(cha)\b"]


class TreebankWordTokenizer:
    """
    The Treebank tokenizer uses regular expressions to tokenize text as in
    Penn Treebank. This is the method. It assumes that thetext has already been
    segmented into sentences.
    This tokenizer performs the following steps:
    - split standard contractions, e.g. ``don't`` -> ``do n't`` and ``they'll`` -> ``they 'll``
    - treat most punctuation characters as separate tokens
    - split off commas and single quotes, when followed by whitespace
    - separate periods that appear at the end of line
    """

    # starting quotes
    STARTING_QUOTES = [
        (re.compile(u'([«“‘„]|[`]+)', re.U), r' \1 '),
        (re.compile(r'^\"'), r'``'),
        (re.compile(r'(``)'), r' \1 '),
        (re.compile(r"([ \(\[{<])(\"|\'{2})"), r'\1 `` '),
    ]

    # punctuation
    PUNCTUATION = [
        (re.compile(r'([^\.])(\.)([\]\)}>"\'' u'»”’ ' r']*)\s*$', re.U), r'\1 \2 \3 '),
        (re.compile(r'([:,])([^\d])'), r' \1 \2'),
        (re.compile(r'([:,])$'), r' \1 '),
        (re.compile(r'\.\.\.'), r' ... '),
        (re.compile(r'[;@#$%&]'), r' \g<0> '),
        (
            re.compile(r'([^\.])(\.)([\]\)}>"\']*)\s*$'),
            r'\1 \2\3 ',
        ),  # Handles the final period.
        (re.compile(r'[?!]'), r' \g<0> '),
        (re.compile(r"([^'])' "), r"\1 ' "),
    ]

    # Pads parentheses
    PARENS_BRACKETS = (re.compile(r'[\]\[\(\)\{\}\<\>]'), r' \g<0> ')

    # Optionally: Convert parentheses, brackets and converts them to PTB symbols.
    CONVERT_PARENTHESES = [
        (re.compile(r'\('), '-LRB-'),
        (re.compile(r'\)'), '-RRB-'),
        (re.compile(r'\['), '-LSB-'),
        (re.compile(r'\]'), '-RSB-'),
        (re.compile(r'\{'), '-LCB-'),
        (re.compile(r'\}'), '-RCB-'),
    ]

    DOUBLE_DASHES = (re.compile(r'--'), r' -- ')

    # ending quotes
    ENDING_QUOTES = [
        (re.compile(u'([»”’]+)', re.U), r' \1 '),
        (re.compile(r'"'), " '' "),
        (re.compile(r'(\S)(\'\')'), r'\1 \2 '),
        (re.compile(r"([^' ])('[sS]|'[mM]|'[dD]|') "), r"\1 \2 "),
        (re.compile(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) "), r"\1 \2 "),
    ]

    # List of contractions adapted from Robert MacIntyre's tokenizer.
    _contractions = MacIntyreContractions()
    CONTRACTIONS2 = list(map(re.compile, _contractions.CONTRACTIONS2))
    CONTRACTIONS3 = list(map(re.compile, _contractions.CONTRACTIONS3))

    def tokenize(self, text, convert_parentheses=False, return_str=False):
        for regexp, substitution in self.STARTING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp, substitution in self.PUNCTUATION:
            text = regexp.sub(substitution, text)

        # Handles parentheses.
        regexp, substitution = self.PARENS_BRACKETS
        text = regexp.sub(substitution, text)
        # Optionally convert parentheses
        if convert_parentheses:
            for regexp, substitution in self.CONVERT_PARENTHESES:
                text = regexp.sub(substitution, text)

        # Handles double dash.
        regexp, substitution = self.DOUBLE_DASHES
        text = regexp.sub(substitution, text)

        # add extra space to make things easier
        text = " " + text + " "

        for regexp, substitution in self.ENDING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp in self.CONTRACTIONS2:
            text = regexp.sub(r' \1 \2 ', text)
        for regexp in self.CONTRACTIONS3:
            text = regexp.sub(r' \1 \2 ', text)

        # We are not using CONTRACTIONS4 since
        # they are also commented out in the SED scripts
        # for regexp in self._contractions.CONTRACTIONS4:
        #     text = regexp.sub(r' \1 \2 \3 ', text)

        return text if return_str else text.split()


_treebank_word_tokenizer = TreebankWordTokenizer()

def word_tokenize(text, language='english', preserve_line=False):
    sentences = [text] if preserve_line else sent_tokenize(text, language)
    return [token for sent in sentences
            for token in _treebank_word_tokenizer.tokenize(sent)]

__all__ = ['word_tokenize']
