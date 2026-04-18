"""Evaluate pywsd WSD methods against the ``alvations/pywsd-datasets``
test sets on HuggingFace Hub.

For each test instance:

1. Build the context string from its ``tokens``,
2. Ask a pywsd method for the disambiguated sense of the target,
3. Count a hit if the returned ``Synset.id`` is in the gold
   ``sense_ids_wordnet`` list (list-valued to handle multi-gold +
   synset-split cases).

Instances where the dataset build failed to resolve any OEWN id for
the gold PWN 3.0 sense key (empty ``sense_ids_wordnet``) are excluded
from both numerator and denominator, and reported separately.

Usage::

    pip install pywsd datasets
    python -m nltk.downloader punkt_tab averaged_perceptron_tagger_eng wordnet
    python -c "import wn; wn.download('oewn:2024')"

    python experiments/evaluate.py                          # all eval configs
    python experiments/evaluate.py --configs en-senseval2-aw
    python experiments/evaluate.py --methods simple_lesk first_sense
    python experiments/evaluate.py --limit 200              # smoke
    python experiments/evaluate.py --out results.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


# Test-only configs in alvations/pywsd-datasets.
TEST_CONFIGS: dict[str, str] = {
    "en-senseval2-aw":       "test",
    "en-senseval3-aw":       "test",
    "en-semeval2007-aw":     "test",
    "en-semeval2013-aw":     "test",
    "en-semeval2015-aw":     "test",
    "en-senseval2_ls":       "test",
    "en-senseval3_ls":       "test",
    "en-semeval2007_t17_ls": "test",
}


def load_rows(config: str, split: str) -> list[dict]:
    """Pull a split directly from HuggingFace Hub."""
    from datasets import load_dataset
    ds = load_dataset("alvations/pywsd-datasets", config)
    return list(ds[split])


def detokenize(tokens: list[str]) -> str:
    return " ".join(tokens).replace("_", " ")


def _wn_pos(pos: str) -> str | None:
    return pos if pos in ("n", "v", "a", "r") else None


def run_method(method: str, sentence: str, lemma: str, pos: str | None):
    from pywsd.lesk import simple_lesk, adapted_lesk, cosine_lesk, original_lesk
    from pywsd.similarity import max_similarity
    from pywsd.baseline import first_sense, random_sense, max_lemma_count

    if method == "simple_lesk":
        return simple_lesk(sentence, lemma, pos=pos)
    if method == "adapted_lesk":
        return adapted_lesk(sentence, lemma, pos=pos)
    if method == "cosine_lesk":
        return cosine_lesk(sentence, lemma, pos=pos)
    if method == "original_lesk":
        return original_lesk(sentence, lemma)
    if method.startswith("max_similarity_"):
        opt = method.removeprefix("max_similarity_")
        return max_similarity(sentence, lemma, option=opt, pos=pos)
    if method == "first_sense":
        try:
            return first_sense(lemma, pos=pos)
        except Exception:
            return None
    if method == "random_sense":
        try:
            return random_sense(lemma, pos=pos)
        except Exception:
            return None
    if method == "max_lemma_count":
        return max_lemma_count(lemma)
    raise ValueError(f"unknown method {method!r}")


DEFAULT_METHODS: list[str] = [
    "first_sense",
    "random_sense",
    "max_lemma_count",
    "original_lesk",
    "simple_lesk",
    "adapted_lesk",
    "cosine_lesk",
    "max_similarity_path",
    "max_similarity_wup",
    "max_similarity_lch",
    "max_similarity_res",
    "max_similarity_jcn",
    "max_similarity_lin",
]


def evaluate_one(rows: list[dict], method: str, limit: int | None = None) -> dict:
    total = 0
    correct = 0
    skipped_nogold = 0
    errors = 0
    t0 = time.time()
    n = len(rows) if limit is None else min(limit, len(rows))
    for i in range(n):
        row = rows[i]
        gold = row.get("sense_ids_wordnet") or []
        if not gold:
            skipped_nogold += 1
            continue
        sentence = detokenize(row["tokens"])
        lemma = row["target_lemma"]
        pos = _wn_pos(row["target_pos"])
        try:
            pred = run_method(method, sentence, lemma, pos)
        except Exception:
            errors += 1
            continue
        if pred is None:
            errors += 1
            continue
        pid = getattr(pred, "id", None)
        if pid is None:
            errors += 1
            continue
        total += 1
        if pid in gold:
            correct += 1
    elapsed = time.time() - t0
    acc = correct / total if total else 0.0
    return {
        "method": method,
        "total": total,
        "correct": correct,
        "accuracy": acc,
        "skipped_nogold": skipped_nogold,
        "errors": errors,
        "elapsed_sec": elapsed,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--configs", nargs="*", default=list(TEST_CONFIGS))
    ap.add_argument("--methods", nargs="*", default=DEFAULT_METHODS)
    ap.add_argument("--limit", type=int, default=None,
                    help="max rows per config (for quick runs)")
    ap.add_argument("--out", type=Path, default=None,
                    help="JSONL results dump (one row per config x method)")
    args = ap.parse_args(argv)

    # One-time WordNet handle / lexicon download.
    from pywsd._wordnet import _get
    _get()

    results: list[dict] = []
    for config in args.configs:
        split = TEST_CONFIGS.get(config)
        if split is None:
            print(f"skip non-test config: {config}", file=sys.stderr)
            continue
        rows = load_rows(config, split)
        print(f"\n## {config}/{split}   ({len(rows)} rows)")
        print(f"{'method':<22} {'acc':>7} {'n':>6} {'err':>5} {'nogold':>7} {'sec':>7}")
        for method in args.methods:
            r = evaluate_one(rows, method, limit=args.limit)
            r.update({"config": config, "split": split})
            results.append(r)
            print(f"{method:<22} {r['accuracy']*100:>6.2f}% {r['total']:>6} "
                  f"{r['errors']:>5} {r['skipped_nogold']:>7} "
                  f"{r['elapsed_sec']:>6.1f}s", flush=True)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as fh:
            for r in results:
                fh.write(json.dumps(r) + "\n")
        print(f"\nwrote {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
