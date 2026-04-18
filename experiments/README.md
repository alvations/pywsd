# experiments/

Reproducible benchmarks of pywsd's algorithms against the unified
[`alvations/pywsd-datasets`](https://huggingface.co/datasets/alvations/pywsd-datasets)
test splits. **Not** part of the installable pywsd package — these
scripts live here so anyone can re-run the numbers without re-deriving
the evaluation pipeline.

## Files

* `evaluate.py` — runs each pywsd method against each test config on
  the HuggingFace Hub dataset and records accuracy.
* `report.py` — aggregates the JSONL results into a method × config
  markdown table.
* `results_lesk.jsonl` — raw run output: Lesk family + baselines across
  the 5 Raganato all-words evaluation sets (pywsd 1.3.0, April 2026).
* `results_maxsim.jsonl` — max_similarity metrics on SemEval-2007 (the
  smallest eval set — these metrics are ~500 ms/instance so only run
  over the 455-row set in this snapshot).

## Setup

```bash
pip install pywsd datasets
python -m nltk.downloader punkt_tab averaged_perceptron_tagger_eng wordnet
python -c "import wn; wn.download('oewn:2024')"
```

## Run

```bash
# All defaults: every method, every all-words eval config.
python experiments/evaluate.py --out experiments/results_lesk.jsonl

# Subsets:
python experiments/evaluate.py --configs en-senseval2-aw --limit 200

# Aggregate:
python experiments/report.py --files experiments/results_lesk.jsonl \
                                      experiments/results_maxsim.jsonl
```

## Protocol

* Target senses in `pywsd-datasets` are OEWN 2024 synset IDs
  (`oewn-<offset>-<pos>`), mapped from the original PWN 3.0 sense keys
  via `wn.compat.sensekey`.
* A prediction counts as correct if the returned `Synset.id` is any
  member of the gold `sense_ids_wordnet` list (handles multi-gold and
  synset-split tolerance).
* Instances where the PWN → OEWN map produced no target (empty gold
  list) are excluded from both numerator and denominator and reported
  in the `nogold` column.
* The `errors` column counts instances where the method raised, or
  returned `None`, or returned something without an `.id` attribute.

## Results — Lesk family + baselines

Across the 5 Raganato all-words evaluation configs (pywsd 1.3.0,
`oewn:2024`, `wikipedia`-corpus IC).

| method | SE2007 (AW) | SE2013 (AW) | SE2015 (AW) | Senseval-2 | Senseval-3 |
|---|---:|---:|---:|---:|---:|
| `first_sense`      | 52.76 | 57.65 | **64.61** | **60.62** | **61.46** |
| `random_sense`     | 23.73 | 36.28 | 42.20 | 40.05 | 34.14 |
| `max_lemma_count`  | 32.95 | 56.27 | 49.85 | 50.48 | 47.15 |
| `original_lesk`    | 15.65 | 36.49 | 34.03 | 34.23 | 28.37 |
| `simple_lesk`      | **47.70** | 55.34 | 61.90 | 58.64 | 55.19 |
| `adapted_lesk`     | 47.00 | 55.34 | 60.98 | 57.19 | 54.79 |
| `cosine_lesk`      | 32.03 | 44.72 | 48.11 | 45.67 | 41.38 |

Cells are accuracy % (higher is better). Instance counts per config:
SemEval-2007 455 (fine-grained), SemEval-2013 1,644, SemEval-2015
1,022, Senseval-2 2,282, Senseval-3 1,850.

### Reading

* `first_sense` (most-frequent-sense heuristic over OEWN's first-sense
  ordering) wins every config. Knowledge-based Lesk variants come
  within 2–4 percentage points but never beat MFS — the well-known
  difficulty of all-words WSD with unsupervised signals.
* `simple_lesk` ≥ `adapted_lesk` ≥ `cosine_lesk` holds on every
  config. Adapted Lesk's wider signature (holonyms/meronyms/similar)
  slightly hurts on Senseval-2 and -3 — more noise than signal.
* `original_lesk` (1986, definition-only overlap) collapses on the
  fine-grained SemEval-2007 (15.65 %) as expected.
* `max_lemma_count` is a surprisingly strong MFS proxy on SemEval-2013
  (56.27 %, within ~1 pp of `first_sense`) but weak on the fine-grained
  SemEval-2007 (32.95 %) where OEWN's per-sense counts are sparse.

## Results — max_similarity (information-content family)

Computed on SemEval-2007 all-words (455 rows) only, because each
similarity-option run takes ~14 minutes per metric on this corpus
(quadratic over candidate × context synsets).

*(Results will be appended here as the sweep finishes. See
`results_maxsim.jsonl` for raw JSON output.)*

## Reproducibility

Results above were generated with:

* `pywsd==1.3.0`
* `wn==1.1.0`, lexicon `oewn:2024`
* `alvations/pywsd-datasets` built from
  [v0.2.0](https://github.com/alvations/pywsd-datasets/releases/tag/v0.2.0),
  which pins the Raganato bundle via a GitHub release mirror.
* Python 3.12, macOS.

Re-run with the exact commands above; scores should be within floating
noise unless OEWN or the Raganato mirror moves under you.

## What's not here (yet)

* Ranked-list metrics (MAP / first-n accuracy with `nbest=True`).
* Per-POS breakdown.
* Evaluation on the UFSAC lexical-sample test splits
  (`en-senseval2_ls`, `en-senseval3_ls`, `en-semeval2007_t17_ls`).
  Lexical-sample WSD has a different protocol — confusion per target
  lemma — that isn't reflected in this script's aggregate accuracy.

Contributions welcome.
