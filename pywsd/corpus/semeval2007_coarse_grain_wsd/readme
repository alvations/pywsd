Semeval-2007: English coarse-grained all words task
(http://lcl.di.uniroma1.it/coarse-grained-aw/index.html)
=================================

Files provided:

- readme.txt (this file)
- coarse-all-words.dtd (the dtd for semeval coarse-grained all words task)
- eng-coarse-all-words.xml (the test set)
- sample_answer_file.ans (a sample answer file)
- wsj_0105.mrg, wsj_0186.mrg, wsj_0239.mrg
  (WSJ texts from the Penn Treebank II)
- Computer_programming.txt 
  (the "computer programming" Wikipedia entry)
- Masaccio_Knights_of_the_Art_by_Amy_Steedman.txt 
  (an excerpt of Amy Steedman's stories of painters)

Lexicon
--------------

The lexicon used is WordNet 2.1 (http://wordnet.princeton.edu).
We encourage participants to exploit the coarse-grained sense inventory
accessible from the task page and downloadable directly from: 
http://lcl.di.uniroma1.it/coarse-grained-aw/sense_inventory.tar.gz

Corpus
--------------

The corpus consists of 5 texts: d001, d002 and d003 are 
Wall Street Journal texts from the Penn Treebank II, 
d004 is the Wikipedia entry on computer programming
(http://en.wikipedia.org/wiki/Computer_programming),
d005 is an excerpt of Amy Steedman's "Knights of the Art"
(stories of Italian painters).

Answer Format
--------------

Your results need to be uploaded in a single tarball. Please use tar
and gzip, or zip to create the tarball. Your tarball should contain 
a single file adhering to the answer format (a sample of this file
is provided in this distribution).
Each answer should consist of zero or one sensekey from WordNet 2.1 
(multiple senses must be avoided). Notice that there is always a 
correct sense for each word instance, as we removed from the 
test set those word instances for which the appropriate sense 
was not found. As a result, monosemous words must always be 
assigned their only sense as a correct answer (the sample file 
reports 5 of these).
Omitting an answer is equivalent to providing zero sensekeys for
the corresponding word instance.

Compound Words and Multi-Word Expressions
--------------

The test set explicitly provides the lemma associated with each word
instance, so as to avoid problems with the recognition of compound words
and multi-word expressions. Sensekeys specified in the answer file
must be senses of the given lemma.

Miscellanea
--------------

The ID attributes of <instance> elements are *not* pointers to the TreeBank files,
but they indicate the position of a word instance within a sentence and document:
e.g. "d001.s003.t006" refers to document #1, sentence #3, tagged word #6.

If you wish to submit more than one system please contact us 
(in accordance with the Semeval rules for participants 
http://nlp.cs.swarthmore.edu/semeval/participants.shtml#rules). 

Thank you for your interest in this task. Enjoy!

Roberto Navigli and Ken Litkowski
