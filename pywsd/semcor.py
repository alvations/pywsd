#!/usr/bin/env python -*- coding: utf-8 -*-

import os, io
from collections import namedtuple, defaultdict
from itertools import chain

from BeautifulSoup import BeautifulSoup as bsoup
from utils import remove_tags, semcor_to_synset, offset_to_synset

Instance = namedtuple('instance', 'id, term, context_sent, context_para')

class SemCorpus:
    def __init__(self):
        self.path = 'data/semcor3.0_naf/'
    
    
    def fileids(self, flatten=True):
        """ Returns files from English SemCor. """
        semcor_files =  [[j+'/'+k for k in sorted(os.listdir(j))] for j in 
                         sorted([os.path.join(self.path,i) 
                                 for i in os.listdir(self.path)])]
        semcor_files = list(chain(*semcor_files)) if flatten else semcor_files
        return semcor_files
        
    
    def read_file(self, filename):
        """
        Reads a single SemCor file in NLP Annotation Format (NAF).
        """
        with io.open(filename, 'r') as fin:
            xml = fin.read()
            text = bsoup(xml).find('text')
            terms = bsoup(xml).find('terms')
            
            sentences = defaultdict(list)
            paragraphs = defaultdict(list)
            
            # Gets the term layer.
            Term = namedtuple('term', 'id, pos, lemma, sense, type') 
            termid2sense = {}
            for term in terms.findAll('term'):
                termid = int(term.get('id')[1:])
                term_sense = None
                try:
                    sense = term.findAll('externalref')[-1].get('reference')
                    term_sense = sense[6:] if sense.startswith('eng30-') else sense
                except:
                    pass
                
                t = Term(termid, term.get('pos'), term.get('lemma'), 
                         term_sense, term.get('type'))
                termid2sense[termid] = t
            
            # Gets the text layer.
            Word = namedtuple('word', 'id, text, offset, sentid, paraid, term')
            wordid2meta = {}
            for word in text.findAll('wf'):
                wordid = int(word.get('id')[1:])
                sentid = int(word.get('sent'))
                paraid = int(word.get('para'))
                try:
                    term = termid2sense[wordid]
                except:
                    term = None
                w = Word(wordid, word.text, word.get('offset'), 
                         sentid, paraid, term)
                wordid2meta[wordid] = w
                sentences[sentid].append(wordid)
                paragraphs[paraid].append(sentid)

            return wordid2meta, termid2sense, sentences, paragraphs

    def instances(self, filename):
        """ Access the corpus by sense annotated instances. """
        wordid2meta, termid2sense, sents, paras = self.read_file(filename)
        
        
        for t in termid2sense:
            term = termid2sense[t]
            sentid = wordid2meta[t].sentid
            paraid = wordid2meta[t].paraid
            # Get words in sentence.
            
            sent = [wordid2meta[i].text for i in sorted(sents[sentid])]
            context_sent =  " ".join(sent)
            # Get words in paragraph.
            para = [wordid2meta[i].text for i in sorted(paras[paraid])]
            context_para = " ".join(para)
            context_sent, context_para
            # Give an instance ID by combining filename.para.sent.wid
            instid = ".".join([filename.rpartition('/')[-1][:-4], 
                               'p'+str(paraid), 's'+str(sentid), 'w'+str(t)])
             
            yield Instance(instid, term, context_sent, context_para)
    
    def sentences(self, filename):
        """
        Access the corpus by sentences.
        
        >>> corpus = SemCorpus()
        >>> corpus_files = corpus.fileids()
        >>> file1 = coprus_files[0]
        >>  for sent in corpus.sentences(file1):
        ...     for token in sent:
        ...         print token
        ...         break
        ...     break
        word(id=0, text=u'The', offset=u'0', sentid=1, paraid=1, term=term(id=0, pos=u'DT', lemma=u'the', sense=None, type=u'open'))
        """
        wordid2meta, termid2sense, sents, paras = self.read_file(filename)
        for sentid in sents:
            words = [wordid2meta[w] for w in sents[sentid]] 
            yield words
            
    def __iter__(self):
        """
        # USAGE:
        >>> corpus = SemCorpus()
        >>> for filename, sent in corpus:
        >>>     for token in sent:
        >>>         print token
        """
        for filename in self.fileids():
            for sent in corpus.sentences(filename):
                yield filename, sent
