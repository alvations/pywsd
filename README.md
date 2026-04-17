[![CI](https://github.com/alvations/pywsd/actions/workflows/ci.yml/badge.svg)](https://github.com/alvations/pywsd/actions/workflows/ci.yml)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Falvations%2Fpywsd.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Falvations%2Fpywsd?ref=badge_shield)

pywsd
=====

Python Implementations of Word Sense Disambiguation (WSD) technologies:

* **Lesk algorithms**
  * Original Lesk (Lesk, 1986)
  * Adapted/Extended Lesk (Banerjee and Pederson, 2002/2003)
  * Simple Lesk (with definition, example(s) and hyper+hyponyms)
  * Cosine Lesk (use cosines to calculate overlaps instead of using raw counts)
  <!-- * Enhanced Lesk (Basile et al. 2014) (in wishlist) -->

* **Maximizing Similarity** (see also, [Pedersen et al. (2003)](http://www.d.umn.edu/~tpederse/Pubs/max-sem-relate.pdf))

  * Path-based: path, Wu-Palmer (1994), Leacock-Chodorow (1998)
  * Information-content: Resnik (1995), Jiang-Conrath (1997), Lin (1998)

* **Baselines**
  * Random sense
  * First WordNet sense
  * Highest lemma counts

**Requires Python 3.10+.** Python 2 users: last supported release is `pywsd==1.1.7`.

Install
====

```
pip install -U pywsd
```

On first use pywsd will auto-download the Open English WordNet (`oewn:2024`)
via [`wn`](https://pypi.org/project/wn/) to `~/.wn_data/`. If you prefer to
pre-download:

```
python -c "import wn; wn.download('oewn:2024')"
```

Information-content files for Resnik / Jiang-Conrath / Lin similarity are
bundled with the package (Brown + Wikipedia, computed against `oewn:2024`).
No additional downloads are required for those metrics to work.

Usage
=====

```python
>>> from pywsd.lesk import simple_lesk
>>> sent = 'I went to the bank to deposit my money'
>>> answer = simple_lesk(sent, 'bank', pos='n')
>>> answer
Synset('oewn-08437235-n')
>>> answer.lemmas()
['depository financial institution', 'bank', 'banking concern', 'banking company']
>>> answer.definition()
'a financial institution that accepts deposits and channels the money into lending activities'
```

All-words disambiguation:

```python
>>> from pywsd import disambiguate
>>> disambiguate('I went to the bank to deposit my money')
[('I', None), ('went', Synset('oewn-02659957-v')), ('to', None), ('the', None),
 ('bank', Synset('oewn-08437235-n')), ('to', None), ('deposit', Synset('oewn-...')),
 ('my', None), ('money', Synset('oewn-...'))]
```

With a different similarity metric:

```python
>>> from pywsd.similarity import max_similarity as maxsim
>>> disambiguate('I went to the bank to deposit my money',
...              algorithm=maxsim, similarity_option='wup', keepLemmas=True)
```

Synset signatures (for simple Lesk). Signatures are computed on demand and
memoized with `functools.lru_cache`, so repeated calls in the same process are
essentially free:

```python
>>> from pywsd.lesk import synset_signatures
>>> from pywsd.baseline import first_sense
>>> dog = first_sense('dog', pos='n')
>>> sorted(synset_signatures(dog))[:8]
['bark', 'barker', 'basenji', 'belgian griffon', 'bow-wow', 'breed', ...]
```

Information-content-based similarity (Resnik / Jiang-Conrath / Lin) uses the
bundled Wikipedia IC by default. Swap corpus or install your own frequency
dict:

```python
>>> import pywsd._wordnet
>>> pywsd._wordnet.IC_CORPUS = 'brown'          # switch to bundled Brown IC
>>> # or supply your own (e.g. computed via wn.ic.compute)
>>> # pywsd._wordnet.set_ic(my_freq_dict)
```

Note on synset identifiers: this is OEWN 2024, so synsets are identified
`oewn-<offset>-<pos>` rather than the PWN 3.0 form `bank.n.01`. Use
`synset.lemmas()`, `.definition()`, and `.pos` for human-readable attributes.

***

Cite
====

To cite `pywsd`:

Liling Tan. 2014. Pywsd: Python Implementations of Word Sense Disambiguation (WSD) Technologies [software]. Retrieved from  https://github.com/alvations/pywsd

In `bibtex`:

```
@misc{pywsd14,
author =   {Liling Tan},
title =    {Pywsd: Python Implementations of Word Sense Disambiguation (WSD) Technologies [software]},
howpublished = {https://github.com/alvations/pywsd},
year = {2014}
}
```

***

<!--
| Algorithm  | Citations | Status | Comment |
|:--|:--|:--|:--|
| Original Lesk | (Lesk, 1986) | `pywsd.lesk.original_lesk` | - |
| Adapted/Extended Lesk |  (Banerjee and Pederson, 2002/2003) | `pywsd.lesk.adapted_lesk` | - |
| Simple Lesk | (Tan, 2014) | `pywsd.lesk.simple_lesk` | Uses definitions, examples, lemma_names|
| Cosine Lesk | (Tan, 2014) | `pywsd.lesk.cosine_lesk` | use cosines to calculate overlaps instead of using raw counts|
| Enhanced Lesk | (Basile et al. 2014) | (in wishlist) | - |

-->

References
=========

* Michael Lesk. 1986. Automatic sense disambiguation using machine readable dictionaries: how to tell a pine cone from an ice cream cone. In Proceedings of the 5th annual international conference on Systems documentation (SIGDOC '86), Virginia DeBuys (Ed.). ACM, New York, NY, USA, 24-26. DOI=10.1145/318723.318728 http://doi.acm.org/10.1145/318723.318728

* Satanjeev Banerjee and Ted Pedersen. 2002. An Adapted Lesk Algorithm for Word Sense Disambiguation Using WordNet. In Proceedings of the Third International Conference on Computational Linguistics and Intelligent Text Processing (CICLing '02), Alexander F. Gelbukh (Ed.). Springer-Verlag, London, UK, UK, 136-145.

* Satanjeev Banerjee and Ted Pedersen. 2003. Extended gloss overlaps as a measure of semantic relatedness. In Proceedings of the Eighteenth International
Joint Conference on Artificial Intelligence, pages 805–810, Acapulco.

* Jay J. Jiang and David W. Conrath. 1997. Semantic similarity based on corpus statistics and lexical taxonomy. In Proceedings of International Conference on Research in Computational Linguistics, Taiwan.

* Claudia Leacock and Martin Chodorow. 1998. Combining local context and WordNet similarity for word sense identification. In Fellbaum 1998, pp. 265–283.

* Lee, Yoong Keok, Hwee Tou Ng, and Tee Kiah Chia. "Supervised word sense disambiguation with support vector machines and multiple knowledge sources." Senseval-3: Third International Workshop on the Evaluation of Systems for the Semantic Analysis of Text. 2004.

* Dekang Lin. 1998. An information-theoretic definition of similarity. In Proceedings of the 15th International Conference on Machine Learning, Madison, WI.

* Linlin Li, Benjamin Roth and Caroline Sporleder. 2010. Topic Models for Word Sense Disambiguation and Token-based Idiom Detection. The 48th Annual Meeting of the Association for Computational Linguistics (ACL). Uppsala, Sweden.

* Andrea Moro, Roberto Navigli, Francesco Maria Tucci and Rebecca J. Passonneau. 2014. Annotating the MASC Corpus with BabelNet. In Proceedings of the Ninth International Conference on Language Resources and Evaluation (LREC'14). Reykjavik, Iceland.

* Zhi Zhong and Hwee Tou Ng. 2010. It makes sense: a wide-coverage word sense disambiguation system for free text. In Proceedings of the ACL 2010 System Demonstrations (ACLDemos '10). Association for Computational Linguistics, Stroudsburg, PA, USA, 78-83.

* Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python (1st ed.). O'Reilly Media, Inc..

* Eneko Agirre and Aitor Soroa. 2009. Personalizing PageRank for Word Sense Disambiguation. Proceedings of the 12th conference of the European chapter of the Association for Computational Linguistics (EACL-2009). Athens, Greece.

* P. Resnik. 1995. Using Information Content to Evaluate Semantic Similarity in a Taxonomy. In Proceedings of IJCAI-95. arXiv:cmp-lg/9511007.
