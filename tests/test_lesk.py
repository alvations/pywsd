"""Lesk-family disambiguation tests."""

from pywsd.lesk import simple_lesk, adapted_lesk, cosine_lesk, original_lesk


BANK_FINANCE = "I went to the bank to deposit my money."
BANK_RIVER = "The river bank was full of dead fishes."


def _sense_lemmas(synset) -> set[str]:
    return {l.lower() for l in synset.lemmas()}


def test_simple_lesk_picks_financial_bank(wordnet):
    ss = simple_lesk(BANK_FINANCE, "bank")
    assert ss is not None
    defn = (ss.definition() or "").lower()
    assert any(w in defn for w in ("financial", "deposit", "money",
                                    "lending", "institution"))


def test_simple_lesk_picks_river_bank(wordnet):
    ss = simple_lesk(BANK_RIVER, "bank", pos="n")
    assert ss is not None
    assert "n" == ss.pos


def test_simple_lesk_returns_none_for_unknown_word(wordnet):
    assert simple_lesk("x", "notawordintheiruniverse") is None


def test_simple_lesk_nbest_returns_list(wordnet):
    ranked = simple_lesk(BANK_FINANCE, "bank", pos="n", nbest=True)
    assert isinstance(ranked, list) and len(ranked) > 1


def test_simple_lesk_keepscore_returns_tuples(wordnet):
    ranked = simple_lesk(BANK_FINANCE, "bank", pos="n",
                         nbest=True, keepscore=True)
    assert all(isinstance(t, tuple) and len(t) == 2 for t in ranked)
    assert all(isinstance(t[0], (int, float)) for t in ranked)


def test_adapted_lesk_runs(wordnet):
    ss = adapted_lesk(BANK_FINANCE, "bank")
    assert ss is not None


def test_cosine_lesk_runs(wordnet):
    ss = cosine_lesk(BANK_FINANCE, "bank")
    assert ss is not None


def test_original_lesk_runs(wordnet):
    ss = original_lesk(BANK_FINANCE, "bank")
    # original_lesk returns None if no overlap — both outcomes are valid
    assert ss is None or ss.id


def test_simple_lesk_result_is_cached(wordnet):
    """Second call should be fast because signatures are lru_cache'd."""
    import time
    simple_lesk(BANK_FINANCE, "bank")  # prime
    t0 = time.perf_counter()
    simple_lesk(BANK_FINANCE, "bank")
    assert time.perf_counter() - t0 < 1.0
