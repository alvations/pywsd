#!/usr/bin/env python3
"""Precompute Information Content files for the bundled WordNet lexicon.

Maintainer-only. Writes a pickled frequency dict to ``pywsd/data/``;
pywsd loads it at runtime via :mod:`pywsd._wordnet`.

Corpora supported (``--corpus``):

* ``brown``      — NLTK Brown (~1.1 M tokens). Small but classic.
* ``wikipedia``  — HuggingFace ``wikitext`` / ``wikitext-103-raw-v1``
                   streamed; ~103 M tokens.

Both produce IC compatible with ``wn.similarity.res/jcn/lin``.

Examples::

    python scripts/build_ic.py --corpus brown
    python scripts/build_ic.py --corpus wikipedia
    python scripts/build_ic.py --corpus wikipedia --limit 20000000
"""

from __future__ import annotations

import argparse
import pickle
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from pywsd._ic import build_ic
from pywsd._wordnet import LEXICON, _get

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")


def _brown_tokens():
    try:
        from nltk.corpus import brown
    except LookupError:
        import nltk
        nltk.download("brown", quiet=True)
        from nltk.corpus import brown
    yield from brown.words()


def _wikipedia_tokens(limit: int | None):
    from datasets import load_dataset

    ds = load_dataset(
        "wikitext", "wikitext-103-raw-v1", split="train", streaming=True
    )
    yielded = 0
    for row in ds:
        text = row["text"]
        if not text.strip():
            continue
        for tok in TOKEN_RE.findall(text):
            yield tok
            yielded += 1
            if limit and yielded >= limit:
                return


def build(corpus: str, limit: int | None, out: Path | None) -> Path:
    w = _get()
    print(f"lexicon: {LEXICON}", flush=True)
    print(f"corpus:  {corpus}{'' if not limit else f' (limit={limit:,})'}", flush=True)

    t0 = time.time()
    if corpus == "brown":
        tokens = list(_brown_tokens())
        print(f"loaded {len(tokens):,} Brown tokens in {time.time()-t0:.1f}s",
              flush=True)
    elif corpus == "wikipedia":
        tokens = _wikipedia_tokens(limit)
    else:
        raise SystemExit(f"unknown corpus: {corpus!r}")

    t0 = time.time()
    freq = build_ic(w, tokens)
    print(f"computed IC in {time.time()-t0:.1f}s", flush=True)

    out = out or (HERE.parent / "pywsd" / "data"
                  / f"ic_{LEXICON.replace(':', '-')}_{corpus}.pkl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fh:
        pickle.dump(freq, fh, protocol=pickle.HIGHEST_PROTOCOL)
    size_mb = out.stat().st_size / 1e6
    print(f"wrote {out} ({size_mb:.2f} MB)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", choices=["brown", "wikipedia"],
                    default="wikipedia")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap tokens (wikipedia only)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    build(args.corpus, args.limit, args.out)


if __name__ == "__main__":
    main()
