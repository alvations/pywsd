"""Similarity metrics + max_similarity WSD."""

import pytest

from pywsd._wordnet import wn, _get
from pywsd.similarity import similarity_by_path, similarity_by_infocontent, sim, max_similarity


@pytest.fixture(scope="module")
def animals():
    w = _get()
    return {
        "dog": w.synset("oewn-02086723-n"),
        "cat": w.synset("oewn-02124272-n"),
        "car": w.synsets("car", pos="n")[0],
    }


def test_path_similarity_range(animals):
    d, c = animals["dog"], animals["cat"]
    v = similarity_by_path(d, c, "path")
    assert 0 < v <= 1


def test_wup_similarity_range(animals):
    d, c = animals["dog"], animals["cat"]
    v = similarity_by_path(d, c, "wup")
    assert 0 < v <= 1


def test_lch_same_pos(animals):
    d, c = animals["dog"], animals["cat"]
    assert similarity_by_path(d, c, "lch") > 0


def test_resnik_nonnegative(animals):
    """Regression: bundled IC must never produce negative Resnik values.

    Upstream wn.ic.compute has a multiple-inheritance double-counting bug;
    pywsd._ic.build_ic fixes it.
    """
    d, c = animals["dog"], animals["cat"]
    assert similarity_by_infocontent(d, c, "res") >= 0


def test_lin_in_unit_interval(animals):
    d, c = animals["dog"], animals["cat"]
    v = similarity_by_infocontent(d, c, "lin")
    assert 0 <= v <= 1.0 + 1e-9


def test_dog_cat_more_similar_than_dog_car(animals):
    d, c, car = animals["dog"], animals["cat"], animals["car"]
    assert similarity_by_path(d, c, "path") > similarity_by_path(d, car, "path")
    assert similarity_by_infocontent(d, c, "lin") > \
           similarity_by_infocontent(d, car, "lin")


def test_sim_rejects_unknown_option(animals):
    d, c = animals["dog"], animals["cat"]
    with pytest.raises(ValueError):
        sim(d, c, "made_up_metric")


def test_max_similarity_picks_a_sense(wordnet):
    ss = max_similarity("I went to the bank to deposit my money.", "bank",
                        option="path", pos="n")
    assert ss is not None and ss.pos == "n"
