***
Change Log
=====

**1.3.0 — 2026-04-17**

Breaking changes. Python 3.10+ required. WordNet backend rewritten against
modern `wn>=1.0` (@goodmami) with the Open English WordNet 2024 lexicon;
synset identifiers are now `oewn-<offset>-<pos>` rather than PWN-3.0
`bank.n.01` form. Use `synset.id`, `synset.lemmas()`, `synset.definition()`,
`synset.pos` on the returned objects.

Bugs fixed:
* `utils.remove_tags` — `reduce` was undefined, `.iteritems()` was Py2-only.
* `utils.synset_properties` — double `eval('synset.' + parameter)` replaced
  with `getattr`.
* `utils.penn2morphy` — bare `except:` narrowed to `except KeyError:`.
* `semeval.py` — `from BeautifulSoup import BeautifulSoup` (Py2 package) →
  `bs4`; broken three-line `yield` / stray `unicode()` calls fixed.
* `allwords_wsd.disambiguate` — `surface_words` / `lemmas` / `morphy_poss`
  were unbound when `context_is_lemmatized=True`.
* `similarity.max_similarity` — `sorted((score, synset), …)` crashed on
  tied scores (modern `wn.Synset` is not `<` comparable).
* `pywsd/__init__.py` version string (was `1.2.4` vs `setup.py` `1.2.5`).

Import-time behaviour:
* `__builtins__['wn'] = WordNet(...)` pollution removed; `wn` is now a lazy
  proxy imported explicitly by each module.
* Eager `print('Warming up PyWSD …')` + `simple_lesk('This is a foo bar
  sentence', 'bar')` warmup deleted.
* 80 MB `pywsd/data/signatures/signatures.pkl` no longer bundled. Signatures
  are computed on demand and memoised in-process with `functools.lru_cache`.
* `import pywsd` dropped from ~11 s to ~1.3 s.

Information-content similarity:
* Upstream `wn.ic.compute` v1.1.0 double-counts ancestors reachable via
  multiple inheritance, producing `P(c) > 1` and `IC(c) < 0` (e.g. Brown
  `res(dog, cat) = −0.29`). `pywsd._ic.build_ic` implements Resnik 1995 §3.2
  correctly with a global visited set per source synset.
* `pywsd/data/ic_oewn-2024_brown.pkl` (3.3 MB, ~1 M tokens) and
  `pywsd/data/ic_oewn-2024_wikipedia.pkl` (3.3 MB, ~103 M tokens, via
  HuggingFace `datasets` / `wikitext-103-raw-v1`) are bundled. Wikipedia is
  the default. `scripts/build_ic.py` regenerates them.
* `pywsd._wordnet.set_ic(freq_dict)` overrides the bundled IC.

Packaging:
* `setup.py` (`distutils.core` — removed in Python 3.12) → `pyproject.toml`
  (PEP 621). `setup.py` is now a 3-line shim.
* Runtime deps trimmed: dropped `six`, `pandas`, `numpy`, and the
  `wn==0.0.23` pin; now `nltk>=3.8`, `wn>=1.0,<2`. `beautifulsoup4` moved
  to the `[semeval]` extra.
* GitHub Actions CI (3.10 / 3.11 / 3.12 / 3.13 / 3.14, `pytest -W error`)
  replaces `.travis.yml` + `tox.ini` (which still listed py27).
* Tests consolidated into `tests/`; 33 tests covering lesk, baselines,
  similarity, all-words, and IC correctness.

**17.01.15**
* Official pyWSD version 1.0 announced. 

**14.01.15**
* Added all-words WSD functionality
* Added disambiguate() for all-words WSD

**05.01.15**:
* Removed old `svm.py`.
* Added Merlin Machine Learning library to support SVM. 

**06.11.14**:
* Fixed bugs in original_lesk() and POS checks in simple_lesk()

**25.10.14**:
* Added corpus readers for SemEval-2007 coarse-grain WSD data and SemCor

**29.05.14** (user request):
* Automatically lemmatize `ambiguous_word` parameter because without it being a lemma, `wn.synsets(ambiguous_word)` breaks the system.

**15.05.14** (bugfix):
* Added try-excepts to allow old NLTK Synset properties.

**15.04.14**: 

* Changed `Synset` properties to methods adhering to new `NLTK` version (see see http://goo.gl/hO79KO)
* Added N-best results, `pywsd` now outputs ranked list of synsets (possible with normalized scores too), see test_wsd.py


**03.04.14**:
* Added similarity based WSD methods.

