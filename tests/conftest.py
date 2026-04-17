"""Shared fixtures. Ensures NLTK + WordNet resources are available."""

import pytest


def _ensure_nltk_data():
    import nltk
    for pkg in ("punkt_tab", "averaged_perceptron_tagger_eng",
                "wordnet", "brown"):
        try:
            nltk.data.find(pkg)
        except LookupError:
            nltk.download(pkg, quiet=True)


@pytest.fixture(scope="session", autouse=True)
def _nltk():
    _ensure_nltk_data()


@pytest.fixture(scope="session")
def wordnet():
    """The shared lazy WordNet shim (auto-downloads the lexicon if missing)."""
    from pywsd._wordnet import wn, _get
    _get()  # trigger lexicon download if needed
    return wn
