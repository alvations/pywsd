Quick reference
===============

### Similarity between synsets

```python
>>> from pywsd._wordnet import wn
>>> law = wn.synsets("law")[0]         # Synset('oewn-08458195-n')
>>> doc = wn.synsets("document")[0]    # Synset('oewn-06481744-n')

>>> from pywsd.similarity import similarity_by_path
>>> similarity_by_path(law, doc, option="path")
0.125
>>> similarity_by_path(law, doc, option="wup")
0.36363636363636365
>>> similarity_by_path(law, doc, option="lch")    # requires same POS
2.538973871058276
```

Information-content metrics (Resnik / Jiang-Conrath / Lin) are backed by the
bundled Wikipedia IC file; nothing extra to install:

```python
>>> from pywsd.similarity import similarity_by_infocontent
>>> similarity_by_infocontent(law, doc, option="res")
1.8...
>>> similarity_by_infocontent(law, doc, option="lin")
0.3...
```

### Max-similarity WSD over a sentence

```python
>>> from pywsd.similarity import max_similarity
>>> max_similarity("The law is certain the law is absolute", "law", option="res")
Synset('oewn-...-n')
>>> max_similarity("The law is certain the law is absolute", "law", option="path")
Synset('oewn-...-n')
```

### Baseline: most frequent sense

```python
>>> from pywsd.baseline import max_lemma_count, first_sense
>>> max_lemma_count("dog")
Synset('oewn-02086723-n')
>>> max_lemma_count("law").definition()
'the collection of rules imposed by authority'
```

Counts come from whatever corpus the installed WordNet lexicon exposes via
`Sense.counts()`. OEWN 2024 ships with limited per-sense counts, so results
often match `first_sense` — that is the documented fallback.

### Signatures

Signatures (bag-of-words from gloss, examples, hyper/hyponyms, and for
`adapted_lesk` also holonyms/meronyms/similar-tos) are computed on demand and
memoised with `functools.lru_cache`:

```python
>>> from pywsd.lesk import synset_signatures, signatures
>>> law = max_lemma_count("law")

>>> synset_signatures(law)            # Synset -> set[str]
{'administrative law', 'authority', 'rule', 'allow', 'international law', ...}

>>> signatures("law")                 # str -> { Synset: set[str], ... }
{Synset('oewn-08458195-n'): {...},
 Synset('oewn-05884120-n'): {...},
 ...}
```

### Lesk family — comparison

```python
>>> sent = "The law is certain the law is absolute"
>>> from pywsd.lesk import simple_lesk, adapted_lesk, cosine_lesk

>>> simple_lesk(sent, "enforce")
Synset('oewn-02565990-v')
>>> adapted_lesk(sent, "enforce")
Synset('oewn-02565990-v')
>>> cosine_lesk(sent, "enforce")
Synset('oewn-02565990-v')
```

### All-words WSD

```python
>>> from pywsd import disambiguate
>>> disambiguate("I went to the bank to deposit my money")
[('I', None), ('went', Synset('oewn-02659957-v')), ('to', None), ('the', None),
 ('bank', Synset('oewn-08437235-n')), ('to', None), ('deposit', Synset(...)),
 ('my', None), ('money', Synset(...))]
```

### Document cosine similarity

```python
>>> from pywsd.cosine import cosine_similarity
>>> cosine_similarity("I like cats", "I enjoy cats")
0.666...
```

### Synset identifiers

This is OEWN 2024, so synsets are identified as `oewn-<offset>-<pos>` rather
than the old PWN 3.0 `bank.n.01` form. Use `synset.id`, `synset.lemmas()`,
`synset.pos`, and `synset.definition()` for the human-readable surface.

### Regenerate bundled IC

```
python scripts/build_ic.py --corpus brown
python scripts/build_ic.py --corpus wikipedia
```

Writes `pywsd/data/ic_oewn-2024_<corpus>.pkl`.
