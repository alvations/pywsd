#!/usr/bin/env python -*- coding: utf-8 -*-

import os, io
from collections import namedtuple

from BeautifulSoup import BeautifulSoup as bsoup
from utils import remove_tags

class SemEval2007_Coarse_WSD:
    """
    Object to load data from SemEval-2007 Coarse-grain all-words WSD task.
    
    USAGE:
    
    >>> coarse_wsd = SemEval2007_Coarse_WSD()
    >>> for inst, sent, docs in coarse_wsd:
    ...     print inst
    ...     print inst.id, inst.lemma, inst.word
    ...     break
    instance(id=u'd001.s001.t001', lemma=u'editorial', word=u'editorial')
    d001.s001.t001 editorial editorial
    """
    def __init__(self):
        self.path = 'corpus/semeval2007_coarse_grain_wsd/'
        self.test_file = self.path + 'coarse_all_word.xml'
        
    def fileids(self):
        """ Returns files from SemEval2007 Coarse-grain All-words WSD task. """
        return [os.path.join(self.path,i) for i in os.listdir(self.path)]
    
    def sents(self, filename=None):
        """
        Returns the file, line by line. Use test_file if no filename specified.
        """
        filename = filename if filename else self.test_file 
        with io.open(filename, 'r') as fin:
            for line in fin:
                yield line.strip()

    def test_instances(self):
        """
        Returns the test instances from SemEval2007 Coarse-grain WSD task.
        """
        Instance = namedtuple('instance', 'id, lemma, word')
        test_file = io.open(self.test_file, 'r').read()
        for text in bsoup(test_file).findAll('text'):
            textid = text['id']
            document = " ".join([remove_tags(i) for i in str(text).split('\n') 
                                 if remove_tags(i)])
            for sent in text.findAll('sentence'):
                sentence =  " ".join([remove_tags(i) for i in 
                                      str(sent).split('\n') if remove_tags(i)])
                for instance in sent.findAll('instance'):
                    instid = instance['id']
                    lemma = instance['lemma']
                    word = instance.text
                    inst = Instance(instid, lemma, word)
                    yield inst, unicode(sentence), unicode(document) 
    
    def __iter__(self):
        """ Iterator function, duck-type of test_instances() """
        self.test_instances()
