Informal Benchmarks
===================

This file contains informal benchmarks to justify design decisions.


Zero-warmup import + in-process `lru_cache` for signatures
---------------------------------------------------------

Up to `pywsd==1.2.4`, `import pywsd` eagerly loaded a ~80 MB `signatures.pkl`
and ran a `simple_lesk('This is a foo bar sentence', 'bar')` warmup call.
Import took ~11 s and the pickle was pinned against PWN 3.0 synset names.

From `pywsd==1.2.5`:

* No import-time WordNet loading.
* No bundled signature pickle.
* Signatures are computed on demand and memoized with `functools.lru_cache`
  keyed by `(synset_id, options)`.

Measured on macOS, Python 3.12, `oewn:2024`:

```
$ python -c "import time; t=time.time(); import pywsd; print(time.time()-t)"
1.28                                          # was ~11.0 s

# first simple_lesk in a fresh process (opens WordNet sqlite + computes signatures)
simple_lesk('I went to the bank to deposit my money', 'bank', pos='n')   12.3 s

# second call (lru_cache hit)
simple_lesk('I went to the bank to deposit my money', 'bank', pos='n')   0.019 s

# 100 Brown sentences disambiguated with simple_lesk:
disambiguate(...)                             ~5 s total after warm-up
```

Speedup over the `from_cache=False` path in `pywsd==1.1.7` (see the history of
this file) remains effectively unchanged: the in-memory cache matches the old
on-disk pickle on repeat calls while dropping the startup penalty and the
disk-size cost.


Information Content correctness
-------------------------------

`wn.ic.compute` in upstream `wn==1.1.0` double-counts ancestors reachable via
multiple inheritance paths (Resnik 1995 §3.2 specifies each ancestor receives
the word's distributed weight *once* per source synset). The inflation is
severe enough that some root synsets exceed the POS total, producing
`P(c) > 1` and `IC(c) < 0`. Concretely:

```
upstream compute (oewn:2024, Brown, buggy):
  entity noun freq     = 400,387
  noun POS total (None) = 298,219
  ratio                 = 1.34      <- should be ≤ 1

  res(dog, cat)         = -0.29     <- should be ≥ 0 by definition

pywsd._ic.build_ic (oewn:2024, Brown, fixed):
  entity noun freq     = 291,829
  noun POS total (None) = 291,829
  ratio                 = 1.00      <- correct root convergence

  res(dog, cat)         = 7.69
  lin(dog, cat)         = 0.87
  jcn(dog, cat)         = 0.45
```

The fix is a one-line change: a *global* visited set per source synset
replaces the per-branch `seen` set in the agenda loop. See `pywsd/_ic.py`.


IC corpus choice: Brown vs Wikipedia
------------------------------------

Both are bundled. Wikipedia is the default because of coverage.

| Pair              | Brown res / lin | Wikipedia res / lin |
|-------------------|-----------------|---------------------|
| dog / cat         | 7.69 / 0.87     | 7.18 / 0.85         |
| dog / kitten      | 5.01 / 0.51     | 4.76 / 0.47         |
| cat / kitten      | 5.01 / 0.50     | 4.76 / 0.46         |
| dog / car         | 2.08 / 0.26     | 2.05 / 0.26         |

* Brown: NLTK corpus, **1.16 M tokens** → ~292k noun tokens contributing to IC.
  Ranking and ratios look correct; rare synsets sit closer to the smoothing
  floor than ideal.
* Wikipedia: `wikitext-103-raw-v1` via HuggingFace `datasets`, **~103 M
  tokens** → ~27.7 M noun tokens. Smoothing is negligible next to real counts;
  lower-variance IC at the cost of a one-time 12-minute compute on the
  maintainer side.

Both pickles are ~3.3 MB and ship with the package. Regenerate with
`scripts/build_ic.py --corpus {brown,wikipedia}`.
