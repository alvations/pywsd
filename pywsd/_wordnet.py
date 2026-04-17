"""Modern ``wn`` shim.

Exposes the attribute/method surface that the rest of pywsd expects
(``wn.synsets(...)``, ``wn.path_similarity(...)``, ...) while delegating to the
current PyPI ``wn`` package (>=1.0) by @goodmami.

The WordNet database is opened on first access and auto-downloaded if missing.
No warmup at import time.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import wn as _wn_pkg
from wn import similarity as _sim

LEXICON = "oewn:2024"
IC_CORPUS = "wikipedia"
IC_CACHE_DIR = Path.home() / ".pywsd_cache"
IC_BUNDLED_DIR = Path(__file__).resolve().parent / "data"

_instance: _wn_pkg.Wordnet | None = None
_ic_freq = None


def _get() -> _wn_pkg.Wordnet:
    """Return the shared Wordnet handle, downloading the lexicon if needed."""
    global _instance
    if _instance is None:
        try:
            _instance = _wn_pkg.Wordnet(LEXICON)
        except _wn_pkg.Error:
            _wn_pkg.download(LEXICON)
            _instance = _wn_pkg.Wordnet(LEXICON)
    return _instance


def set_ic(ic) -> None:
    """Install an information-content frequency dict for res/jcn/lin similarity.

    Compute via ``wn.ic.compute(corpus)`` or load via ``wn.ic.load(path)``.
    Overrides the auto-backfilled Brown-corpus IC.
    """
    global _ic_freq
    _ic_freq = ic


def _ic_filename(corpus: str) -> str:
    return f"ic_{LEXICON.replace(':', '-')}_{corpus}.pkl"


def _ic_bundled_path(corpus: str) -> Path:
    return IC_BUNDLED_DIR / _ic_filename(corpus)


def _ic_cache_path(corpus: str) -> Path:
    return IC_CACHE_DIR / _ic_filename(corpus)


def _auto_ic(corpus: str = IC_CORPUS):
    """Load an IC frequency dict, preferring the bundled file.

    Looks in order at:
      1. ``pywsd/data/ic_<lexicon>_<corpus>.pkl`` (ships with the package)
      2. ``~/.pywsd_cache/ic_<lexicon>_<corpus>.pkl`` (built via ``build_ic.py``)

    Raises if neither is present; use :func:`set_ic` to install a custom IC
    or run ``scripts/build_ic.py`` to build one.
    """
    for candidate in (_ic_bundled_path(corpus), _ic_cache_path(corpus)):
        if candidate.exists():
            with open(candidate, "rb") as fh:
                return pickle.load(fh)
    raise RuntimeError(
        f"no IC file found for {LEXICON} + {corpus!r}. "
        f"Install via pywsd._wordnet.set_ic(freq_dict) or run "
        f"scripts/build_ic.py --corpus {corpus}."
    )


def _require_ic():
    global _ic_freq
    if _ic_freq is None:
        _ic_freq = _auto_ic()
    return _ic_freq


def _sim_or(default, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except _wn_pkg.Error:
        return default


class _WnShim:
    """Compatibility surface over modern wn."""

    # --- lookups ---
    def synsets(self, form, pos=None):
        return _get().synsets(form, pos=pos)

    def synset(self, synset_id):
        return _get().synset(synset_id)

    def words(self, form=None, pos=None):
        return _get().words(form=form, pos=pos)

    # --- similarity (graph-based) ---
    def path_similarity(self, s1, s2, if_none_return=0):
        return _sim_or(if_none_return, _sim.path, s1, s2)

    def wup_similarity(self, s1, s2, if_none_return=0):
        return _sim_or(if_none_return, _sim.wup, s1, s2)

    def lch_similarity(self, s1, s2, if_none_return=0, max_depth=20):
        return _sim_or(if_none_return, _sim.lch, s1, s2, max_depth=max_depth)

    # --- similarity (information-content-based) ---
    def res_similarity(self, s1, s2, if_none_return=0):
        return _sim_or(if_none_return, _sim.res, s1, s2, _require_ic())

    def jcn_similarity(self, s1, s2, if_none_return=0):
        return _sim_or(if_none_return, _sim.jcn, s1, s2, _require_ic())

    def lin_similarity(self, s1, s2, if_none_return=0):
        return _sim_or(if_none_return, _sim.lin, s1, s2, _require_ic())

    # --- sensekey lookup ---
    def lemma_from_key(self, sensekey):
        from wn.compat.sensekey import sense_getter

        get = sense_getter(LEXICON)
        sense = get(sensekey)
        if sense is None:
            raise _wn_pkg.Error(f"no sense found for sensekey {sensekey!r}")
        return sense


wn = _WnShim()
