pywsd
=====

Python Implementations of Word Sense Disambiguation (WSD) technologies:

* **Lesk algorithms**
  * Original Lesk (Lesk, 1986)
  * Adapted/Extended Lesk (Banerjee and Pederson, 2002/2003)
  * Simple Lesk (with definition, example(s) and hyper+hyponyms)
  * Cosine Lesk (use cosines to calculate overlaps instead of using raw counts)
  * Enhanced Lesk (Basile et al. 2014) (in wishlist)
  
* **Maximizing Similarity** (see also, http://goo.gl/MG8ZpE)
  * Path similarity (Wu-Palmer, 1994; Leacock and Chodorow, 1998)
  * Information Content (Resnik, 1995; Jiang and Corath, 1997; Lin, 1998)
  
* **Supervised WSD** (in progress)
  * SVM WSD (Lee, Ng and Chia 2004)
  * It Makes Sense (IMS) (Zhong and Ng, 2010) 
 
* **Vector Space Models** (in progress)
  * LSI/LSA
  * Topic Models, LDA (Li et al. 2012)
  * NMF

* **Graph based Models** (in wishlist)
  * Babelfly (Moro et al. 2014)
  * UKB (Agirre and Soroa, 2009)

* **Baselines**
  * Random sense
  * First NLTK sense
  * Highest lemma counts 

(**NOTE**: requires `NLTK`, goto http://nltk.org/install.html. Also, note that as of 30.10.13, NLTK has changed `Synset` object properties to methods, see http://goo.gl/hO79KO)

As a bonus, `pyWSD` comes with an almost native python implementations of several classification algorithms within the `Merlin` machine learning library, see https://github.com/alvations/pywsd/tree/master/merlin


***
Usage
=====

```
$ git clone https://github.com/alvations/pywsd.git 
$ cd pywsd
$ ls
pywsd  README.md  test_wsd.py
$ python
>>> from pywsd.lesk import simple_lesk
>>> sent = 'I went to the bank to deposit my money'
>>> ambiguous = 'bank'
>>> answer = simple_lesk(sent, ambiguous, pos='n')
>>> print answer
Synset('bank.n.09')
>>> print answer.definition()
u'a building in which the business of banking transacted
```

For all-words WSD, try:
```
>>> from pywsd import disambiguate
>>> from pywsd.similarity import max_similarity as maxsim
>>> disambiguate('I went to the bank to deposit my money')
[('I', None), ('went', Synset('run_low.v.01')), ('to', None), ('the', None), ('bank', Synset('depository_financial_institution.n.01')), ('to', None), ('deposit', Synset('deposit.v.02')), ('my', None), ('money', Synset('money.n.03'))]
>>> disambiguate('I went to the bank to deposit my money', algorithm=maxsim, similarity_option='wup', keepLemmas=True)
[('I', 'i', None), ('went', u'go', Synset('sound.v.02')), ('to', 'to', None), ('the', 'the', None), ('bank', 'bank', Synset('bank.n.06')), ('to', 'to', None), ('deposit', 'deposit', Synset('deposit.v.02')), ('my', 'my', None), ('money', 'money', Synset('money.n.01'))]
```

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
howpublished = {https://github.com/alvations/pywsd}},
year = {2014}
}
```

***
License
====

The MIT License (MIT)

Copyright (c) 2014-2015 alvations

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

***
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


