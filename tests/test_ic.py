"""Information Content correctness.

These regress against the upstream ``wn.ic.compute`` bug where ancestors
reachable via multiple inheritance paths receive double-counted weight,
producing ``P(c) > 1`` and ``IC(c) < 0`` (Resnik 1995 forbids negative IC).
"""

import math
import pickle
from pathlib import Path

import pytest

from pywsd._wordnet import _get, IC_BUNDLED_DIR


def _bundled_ic_files():
    return sorted(IC_BUNDLED_DIR.glob("ic_*.pkl"))


@pytest.mark.parametrize("path", _bundled_ic_files(),
                         ids=lambda p: p.stem)
def test_bundled_ic_root_ratio_is_at_most_one(path: Path):
    """freq(root) / freq(None) must be <= 1; >1 means double-counting bug."""
    with open(path, "rb") as fh:
        freq = pickle.load(fh)
    for pos in ("n", "v", "a", "r"):
        total = freq[pos][None]
        if total <= 0:
            continue
        max_synset = max(v for k, v in freq[pos].items() if k is not None)
        assert max_synset / total <= 1.0 + 1e-9, \
            f"{path.name} POS={pos}: max synset freq {max_synset} > total {total}"


@pytest.mark.parametrize("path", _bundled_ic_files(),
                         ids=lambda p: p.stem)
def test_bundled_ic_all_probabilities_valid(path: Path):
    with open(path, "rb") as fh:
        freq = pickle.load(fh)
    for pos in ("n", "v", "a", "r"):
        total = freq[pos][None]
        for sid, f in freq[pos].items():
            if sid is None:
                continue
            p = f / total
            assert 0 < p <= 1 + 1e-9, \
                f"{path.name} {pos}:{sid} probability {p} out of range"


def test_build_ic_fixed_vs_upstream_compute():
    """pywsd._ic.build_ic must never produce negative IC on a small sample.

    Upstream wn.ic.compute can; this is a direct regression guard.
    """
    from pywsd._ic import build_ic
    w = _get()
    # Tiny corpus: enough to exercise the hypernym lattice
    tokens = ["dog", "cat", "run", "bank", "money", "river"] * 20
    freq = build_ic(w, tokens)

    total = freq["n"][None]
    assert total > 0
    for sid, f in freq["n"].items():
        if sid is None:
            continue
        p = f / total
        assert 0 < p <= 1 + 1e-9
        ic = -math.log(p)
        assert ic >= 0
