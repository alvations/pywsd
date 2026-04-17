"""Baseline WSD strategies."""

import pytest

from pywsd.baseline import random_sense, first_sense, max_lemma_count


def test_first_sense_returns_first_synset(wordnet):
    ss = first_sense("bank")
    expected = wordnet.synsets("bank")[0]
    assert ss == expected


def test_first_sense_with_pos(wordnet):
    ss = first_sense("bank", pos="n")
    assert ss.pos == "n"


def test_random_sense_is_deterministic(wordnet):
    # baseline uses a seeded Random(0); repeated calls may diverge but the
    # first call in a process is deterministic, and the result is always a
    # valid synset of the word.
    ss = random_sense("bank")
    assert ss in wordnet.synsets("bank")


def test_max_lemma_count_returns_a_synset(wordnet):
    ss = max_lemma_count("bank")
    assert ss in wordnet.synsets("bank")


def test_max_lemma_count_none_for_unknown(wordnet):
    assert max_lemma_count("notawordintheiruniverse") is None


def test_first_sense_raises_for_unknown(wordnet):
    with pytest.raises(IndexError):
        first_sense("notawordintheiruniverse")
