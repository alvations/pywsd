pywsd
=====

Python Implementations of Word Sense Disambiguation (WSD) technologies:

* **Lesk algorithms**
  * Original Lesk (Lesk, 1986)
  * Adapted/Extended Lesk (Banerjee and Pederson, 2002/2003)
  * Simple Lesk (with definition, example(s) and hyper+hyponyms)
  * Cosine Lesk (use cosines to calculate overlaps instead of using raw counts)
* **Vector Space Models** (in progress)
  * LSI/LSA
  * Topic Models, LDA (Li et al. 2012)
  * NMF
* **Baselines**
  * Random sense
  * First NLTK sense
  * Highest lemma counts 

(**NOTE**: requires `NLTK`, goto http://nltk.org/install.html)

***
Usage
=====

```
$ cd pywsd/
$ ls
baseline.py   cosine.py   lesk.py   README.md   test_wsd.py
$ python
>>> from lesk import simple_lesk
>>> sent = 'I went to the bank to deposit my money'
>>> ambiguous = 'bank'
>>> answer = simple_lesk(sent, ambiguous)
>>> print answer
Synset('depository_financial_institution.n.01')
>>> print answer.definition
a financial institution that accepts deposits and channels the money into lending activities

```



***
References
=========

* Michael Lesk. 1986. Automatic sense disambiguation using machine readable dictionaries: how to tell a pine cone from an ice cream cone. In Proceedings of the 5th annual international conference on Systems documentation (SIGDOC '86), Virginia DeBuys (Ed.). ACM, New York, NY, USA, 24-26. DOI=10.1145/318723.318728 http://doi.acm.org/10.1145/318723.318728

* Satanjeev Banerjee and Ted Pedersen. 2002. An Adapted Lesk Algorithm for Word Sense Disambiguation Using WordNet. In Proceedings of the Third International Conference on Computational Linguistics and Intelligent Text Processing (CICLing '02), Alexander F. Gelbukh (Ed.). Springer-Verlag, London, UK, UK, 136-145.

* Satanjeev Banerjee and Ted Pedersen. 2003. Extended gloss overlaps as a measure of semantic relatedness. In Proceedings of the Eighteenth International
Joint Conference on Artificial Intelligence, pages 805–810, Acapulco.

* Linlin Li, Benjamin Roth and Caroline Sporleder. 2010. Topic Models for Word Sense Disambiguation and Token-based Idiom Detection. The 48th Annual Meeting of the Association for Computational Linguistics (ACL). Uppsala, Sweden.

* Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python (1st ed.). O'Reilly Media, Inc..
