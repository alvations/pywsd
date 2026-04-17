"""Information Content (IC) computation.

Implements Resnik 1995 §3.2 directly. The version bundled with upstream
``wn`` (v1.1.0) double-counts ancestors reachable via multiple inheritance
paths, producing ratios ``freq(c) / freq(None) > 1`` and consequently
negative IC. This module walks each source synset's ancestor lattice
with a **global** visited set so every ancestor receives the word's
distributed weight exactly once per source synset.

Reference
---------
P. Resnik (1995). *Using Information Content to Evaluate Semantic
Similarity in a Taxonomy.* IJCAI-95. arXiv:cmp-lg/9511007.

D. Lin (1998). *An Information-Theoretic Definition of Similarity.*
ICML-98 — depends on the same IC formulation.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

IC_PARTS_OF_SPEECH = ("n", "v", "a", "r")
_ADJ = "a"
_ADJ_SAT = "s"


def build_ic(wordnet, tokens: Iterable[str],
             smoothing: float = 1.0,
             distribute_weight: bool = True) -> dict:
    """Compute an IC frequency mapping compatible with ``wn.similarity``.

    Returns a dict keyed by POS (``'n'``/``'v'``/``'a'``/``'r'``) mapping
    to dicts of ``{synset_id: cumulative_frequency}``. The sentinel key
    ``None`` holds the POS total. Adjective-satellite synsets are folded
    into ``'a'``.
    """
    freq: dict[str, dict] = {pos: {} for pos in IC_PARTS_OF_SPEECH}
    for pos in IC_PARTS_OF_SPEECH:
        for ss in wordnet.synsets(pos=pos):
            freq[pos][ss.id] = smoothing
        freq[pos][None] = smoothing
    for ss in wordnet.synsets(pos=_ADJ_SAT):
        freq[_ADJ][ss.id] = smoothing

    counts = Counter(t.lower() for t in tokens if t and t[0].isalpha())

    hypernym_cache: dict = {}

    for word, count in counts.items():
        synsets = wordnet.synsets(word)
        if not synsets:
            continue
        weight = (count / len(synsets)) if distribute_weight else float(count)

        for ss in synsets:
            pos = ss.pos
            if pos == _ADJ_SAT:
                pos = _ADJ
            if pos not in IC_PARTS_OF_SPEECH:
                continue

            freq[pos][None] += weight

            # Resnik 1995 §3.2: each ancestor gets the weight ONCE per source
            # synset. Use a global visited set across the whole ancestor lattice
            # to avoid the multiple-inheritance double-counting that inflates
            # root nodes above the POS total.
            visited: set[str] = set()
            agenda = [ss]
            while agenda:
                node = agenda.pop()
                nid = node.id
                if nid in visited:
                    continue
                visited.add(nid)
                freq[pos][nid] = freq[pos].get(nid, smoothing) + weight
                if node not in hypernym_cache:
                    hypernym_cache[node] = node.hypernyms()
                agenda.extend(hypernym_cache[node])

    return freq
