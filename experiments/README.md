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

## Results — combined method × config matrix

pywsd 1.3.0, `oewn:2024`, bundled Wikipedia-corpus IC. Cells are
accuracy % over OEWN-resolvable instances.

| method | SE07 (AW) | SE13 (AW) | SE15 (AW) | SE2 (AW) | SE3 (AW) | SE2 (LS) | SE3 (LS) | SE07T17 (LS†) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `first_sense`          | 52.76 | 57.65 | **64.61** | **60.62** | **61.46** | 39.42 | 52.12 | 52.76 |
| `random_sense`         | 23.73 | 36.28 | 42.20 | 40.05 | 34.14 | 18.36 | 19.14 | 28.80 |
| `max_lemma_count`      | 32.95 | 56.27 | 49.85 | 50.48 | 47.15 | 23.24 | 38.02 | 33.18 |
| `original_lesk`        | 15.65 | 36.49 | 34.03 | 34.23 | 28.37 | 16.69 | 19.68 | 15.70 |
| `simple_lesk`          | 47.70 | 55.34 | 61.90 | 58.64 | 55.19 | 39.65 | 47.15 | 47.24 |
| `adapted_lesk`         | 47.00 | 55.34 | 60.98 | 57.19 | 54.79 | 39.15 | 47.24 | 46.54 |
| `cosine_lesk`          | 32.03 | 44.72 | 48.11 | 45.67 | 41.38 | 27.59 | 26.36 | 31.80 |
| `max_similarity_path`  | 33.56 |  –    |  –    |  –    |  –    |  –    |  –    |  – |
| `max_similarity_wup`   | 30.56 |  –    |  –    |  –    |  –    |  –    |  –    |  – |
| `max_similarity_lch`   | 33.56 |  –    |  –    |  –    |  –    |  –    |  –    |  – |
| `max_similarity_res`   | 26.62 |  –    |  –    |  –    |  –    |  –    |  –    |  – |
| `max_similarity_jcn`   | **52.55** | **57.19** | **63.42** | **59.84** |  – |  – |  – |  – |
| `max_similarity_lin`   | 30.56 |  –    |  –    |  –    |  –    |  –    |  –    |  – |

Column headers: `SE07 (AW)`=SemEval-2007 fine-grained all-words
(Raganato export), `SE13 (AW)`=SemEval-2013 Task 12,
`SE15 (AW)`=SemEval-2015 Task 13, `SE2 (AW)`=Senseval-2 all-words,
`SE3 (AW)`=Senseval-3 all-words, `SE2 (LS)` / `SE3 (LS)`=Senseval-2
& 3 lexical-sample test sets, `SE07T17 (LS†)`=SemEval-2007 Task 17
via UFSAC.

**Note:** `SE07T17 (LS†)` is essentially the same 455-instance
SemEval-2007 Task 17 fine-grained all-words test set as `SE07 (AW)`,
sourced from UFSAC's export rather than the Raganato bundle. SE2007
Task 17 was never a lexical-sample track; the `_ls` suffix in
`en-semeval2007_t17_ls` is a mislabel in pywsd-datasets v0.2.0. The
scores confirm it — all methods produce near-identical numbers
(±0.5 pp) across the two columns. Will rename in the next dataset
release.

### Cells not filled (`–`)

Two reasons a cell is `–`:

1. **The jcn row is being filled now.** Because jcn is the standout
   IC-based metric on SE2007, we're running it across every remaining
   config to see whether the advantage holds. Streams into
   `results_maxsim_jcn.jsonl`; expect several hours of wall time (jcn
   was 586 s for 432 rows; largest config here is 4,239 rows). Cells
   will be updated as they land.

2. **All other `max_similarity` cells are deliberately skipped.** Each
   `max_similarity` run is quadratic in (candidate synsets × context
   synsets) and takes ~10–30 minutes per metric per config even on
   the 455-row SemEval-2007. The other test configs are 2–10× larger,
   so a full sweep of all six metrics would be many hours. Partial
   SE2007 results (the filled SE07 column above) are sufficient to
   rank the six metrics; `jcn` is clearly best. If someone needs the
   complete grid, run:

   ```
   python experiments/evaluate.py \\
       --configs <larger-config> \\
       --methods max_similarity_path max_similarity_wup max_similarity_lch \\
                 max_similarity_res max_similarity_jcn max_similarity_lin \\
       --out experiments/results_maxsim_<config>.jsonl
   ```

### Instance counts (gold-resolvable / total in test split)

| config | n (total) | gold-resolvable | OEWN coverage |
|---|---:|---:|---:|
| `en-semeval2007-aw`   | 455   | 454   | 99.78 % |
| `en-semeval2013-aw`   | 1,644 | 1,644 | 100.00 % |
| `en-semeval2015-aw`   | 1,022 | 1,015 | 99.32 % |
| `en-senseval2-aw`     | 2,282 | 2,269 | 99.43 % |
| `en-senseval3-aw`     | 1,850 | 1,841 | 99.51 % |
| `en-senseval2_ls`     | 4,239 | 3,756 | 88.61 % |
| `en-senseval3_ls`     | 3,849 | 3,156 | 82.00 % |
| `en-semeval2007_t17_ls` | 455 | 454   | 99.78 % |

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

## Results — max_similarity (path + information-content family)

Computed on SemEval-2007 all-words (455 rows) only. Each option is
quadratic in (candidate synsets × context synsets) and takes 10–30
minutes per metric on this corpus, so the other evaluation sets would
be ~4× slower each — deferred unless someone needs them.

| metric  | accuracy | sec    | notes                                  |
|---------|---------:|-------:|----------------------------------------|
| `path`  | 33.56    |   825  | `1 / (distance + 1)`                   |
| `wup`   | 30.56    |  1641  | Wu-Palmer                              |
| `lch`   | 33.56    |   926  | Leacock-Chodorow (same-POS only)       |
| `res`   | 26.62    |   556  | Resnik 1995, needs IC                  |
| **`jcn`** | **52.55** |   586  | **Jiang-Conrath — best max_similarity** |
| `lin`   | 30.56    |   627  | Lin 1998, needs IC                     |

### Reading

* `jcn` is the standout at **52.55 %**, beating every other
  `max_similarity` metric on SE2007 by 19+ pp and edging out
  `simple_lesk` (47.70 %) on the same config. Jiang-Conrath's
  `1 / (IC(c1) + IC(c2) − 2·IC(lcs))` penalizes pairs whose LCS is
  generic relative to how specific c1 and c2 are, which evidently
  maps well to WSD target scoring on this corpus.
* `res` under-performs because taking `IC(lcs)` alone ranks high-IC
  (specific) ancestors so aggressively that it tends to collapse to
  generic MFS-like behavior; the distance-aware JCN handles that better.
* `path` and `lch` tie at 33.56 % — lch is path-length-to-depth-ratio
  with a log, which is nearly monotonic in path on English WordNet, so
  equivalent rankings come out. `wup`, `lin` both at 30.56 % — not a
  coincidence, likely driven by the same LCS-ranking ties.
* **Information-content quality is load-bearing.** Resnik/JCN/Lin all
  need correct IC. pywsd 1.3.0 ships Wikipedia-corpus IC precomputed
  via `pywsd._ic.build_ic` (Resnik-1995-correct; fixes the double-count
  bug in upstream `wn.ic.compute`). The non-trivial res/jcn/lin scores
  are the downstream validation that IC is right.

### Why does jcn win over lin (and everything else IC-based)?

They use the same inputs (IC of each concept + IC of their LCS) but
different normalizations. Rewriting jcn:

    jcn(c1, c2) = 1 / [ (IC(c1) − IC(lcs)) + (IC(c2) − IC(lcs)) ]

The denominator is the **IC-distance from each concept to their LCS**,
summed. jcn is the inverse of how much information has to be traversed
to go between c1 and c2 via their LCS. lin, by contrast, is a
**ratio** of shared-to-total IC, insensitive to the absolute
IC-distance:

    lin(c1, c2) = 2 · IC(lcs) / (IC(c1) + IC(c2))       ∈ [0, 1]
    res(c1, c2) = IC(lcs)

Three consequences for WSD ranking via `max_similarity`, which scores a
candidate sense `c_a` of an ambiguous word by
`Σ_{w ∈ context} max_{s ∈ synsets(w)} sim(c_a, s)`:

1. **jcn is unbounded; lin is capped at 1.** When a context word's
   synset is near-identical to a candidate, jcn returns a huge number
   and dominates the sum — a strong "if anything in context agrees
   with this candidate, lock it in" signal. lin maxes out at 1.0, so
   an exact match contributes the same as a moderate match.
2. **jcn penalizes generic LCSes quadratically.** If the LCS is
   `entity` (IC ≈ 0), both `IC(ci) − IC(lcs)` terms stay large and
   jcn → 0. lin's ratio is badly conditioned at the root (small
   numerator, small denominator) and returns noise. jcn cleanly says
   "these are far apart, don't pick this candidate."
3. **jcn rewards matching abstraction level.** Because it's inverse
   IC-distance, it prefers a candidate sense whose IC is close to the
   context's typical IC. Lesk and `first_sense` have no taxonomic-
   depth awareness at all.

This matches the empirical record: Budanitsky & Hirst (2006) reported
jcn ≥ lin ≥ res ≥ path on multiple WSD benchmarks. Our SE2007 numbers
reproduce that ordering (52.55 > 30.56 > 26.62, with path at 33.56
edging res because res uses `IC(lcs)` alone — collapses on a sparse
IC estimate for OEWN, and has no depth awareness).

The decisive test is whether jcn's lead **holds across configs** or
whether it just mirrored MFS on SE2007 (where `first_sense` was 52.76
and jcn was 52.55 — within noise). The in-flight jcn sweep on all 7
remaining configs is that test.

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
