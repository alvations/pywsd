#!/usr/bin/env python -*- coding: utf-8 -*-

import os, io
from collections import namedtuple
from itertools import chain

from BeautifulSoup import BeautifulSoup as bsoup
from utils import remove_tags, semcor_to_synset, offset_to_synset

class SemCorpus:
    def __init__(self):
        self.path = 'corpus/semcor3.0_naf/'
    
    
    def fileids(self, flatten=True):
        """ Returns files from English SemCor. """
        semcor_files =  [[j+'/'+k for k in sorted(os.listdir(j))] for j in 
                         sorted([os.path.join(self.path,i) 
                                 for i in os.listdir(self.path)])]
        semcor_files = list(chain(*semcor_files)) if flatten else semcor_files
        return semcor_files
        
    
    def read_file(self, filename):
        with io.open(filename, 'r') as fin:
            xml = fin.read()
            text = bsoup(xml).find('text')
            terms = bsoup(xml).find('terms')
            
            # Gets the text layer.
            Word = namedtuple('word', 'id, text, offset, sentid, paraid')
            wordid2meta = {}
            for word in text.findAll('wf'):
                wordid = int(word.get('id')[1:])
                w = Word(wordid, word.text, word.get('offset'), 
                         int(word.get('sent')), int(word.get('para')))
                wordid2meta[wordid] = w
            
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

            return wordid2meta, termid2sense

    def instances(self, filename):
        wordid2meta, termid2sense = self.read_file(filename)
        Instance = namedtuple('instance', 'id, lemma, word')
        
        for t in termid2sense:
            term = termid2sense[t]
            sentid = wordid2meta[t].sentid
            paraid = wordid2meta[t].paraid
            # Get words in sentence.
            sent = [i.text for i in sorted(wordid2meta.values()) 
                    if i.sentid == sentid]
            context_sent =  " ".join(sent)
            # Get words in paragraph.
            para = [i.text for i in sorted(wordid2meta.values())
                    if i.paraid ==paraid]
            context_para = " ".join(para)
            context_sent, context_para
            # Give an instance ID by combining filename.para.sent.wid
            instid = ".".join([filename.rpartition('/')[-1][:-4], 
                               'p'+str(paraid), 's'+str(sentid), 'w'+str(t)]) 
            yield instid, term, context_sent, context_para
                
                
x = SemCorpus()
y = x.fileids()[0]
for i in x.instances(y):
    print i