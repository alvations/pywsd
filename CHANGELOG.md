***
Change Log
=====

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

