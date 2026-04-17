"""All-words disambiguation."""

from pywsd.allwords_wsd import disambiguate
from pywsd.lesk import simple_lesk, adapted_lesk, cosine_lesk, original_lesk


def test_disambiguate_returns_word_synset_pairs(wordnet):
    result = disambiguate("The fish swam in the river.")
    assert all(isinstance(t, tuple) and len(t) == 2 for t in result)
    # content words get synsets, stopwords/punct get None
    words = {w for w, _ in result}
    assert {"fish", "swam", "river"} <= words


def test_disambiguate_keep_lemmas(wordnet):
    result = disambiguate("Dogs bark loudly.", keepLemmas=True)
    assert all(isinstance(t, tuple) and len(t) == 3 for t in result)


def test_disambiguate_prefers_none(wordnet):
    result = disambiguate("The fish swam.", prefersNone=True)
    nones = [w for w, s in result if s is None]
    assert "The" in nones or "the" in nones
    assert "." in nones


def test_disambiguate_with_alternate_algorithms(wordnet):
    sent = "Dogs bark loudly."
    for algo in (adapted_lesk, cosine_lesk, original_lesk):
        result = disambiguate(sent, algorithm=algo)
        assert len(result) > 0


def test_disambiguate_context_is_lemmatized(wordnet):
    # Passing already-lemmatized context
    result = disambiguate("dog bark loud",
                          context_is_lemmatized=True,
                          algorithm=simple_lesk)
    assert len(result) == 3
