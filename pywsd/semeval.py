#!/usr/bin/env python -*- coding: utf-8 -*-

import os, io
from collections import namedtuple

from BeautifulSoup import BeautifulSoup as bsoup
from utils import remove_tags, semcor_to_synset

class SemEval2007_Coarse_WSD:
    """
    Object to load data from SemEval-2007 Coarse-grain all-words WSD task.
    
    USAGE:
    
    >>> coarse_wsd = SemEval2007_Coarse_WSD()
    >>> for inst, ans, sent, doc in coarse_wsd:
    ...     print inst
    ...     print inst.id, inst.lemma, inst.word
    ...     print ans.sensekey
    ...     break
    instance(id=u'd001.s001.t001', lemma=u'editorial', word=u'editorial')
    d001.s001.t001 editorial editorial
    [u'editorial%1:10:00::']
    """
    def __init__(self):
        self.path = 'data/semeval2007_coarse_grain_wsd/'
        self.test_file = self.path + 'eng-coarse-all-words.xml'
        self.test_ans = self.path + 'dataset21.test.key'
        
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

    def get_answers(self):
        """
        Returns a {(key,value), ...} dictionary of {(instance_id,Answer),...)}
        >>> coarse_wsd = SemEval2007_Coarse_WSD()
        >>> inst2ans = coarse_wsd.get_answers()
        >>> for inst in inst2ans:
        ...    print inst, inst2ans[inst
        ...    break
        """
        inst2ans = {}
        Answer = namedtuple('answer', 'sensekey, lemma, pos')
        with io.open(self.test_ans, 'r') as fin:
            for line in fin:
                line, _, lemma = line.strip().rpartition(' !! ')
                lemma, pos = lemma[6:].split('#')
                textid, _, line = line.partition(' ')
                instid, _, line = line.partition(' ')
                sensekey = line.split()
                # What to do if there is no synset to convert to...
                # synsetkey = [semcor_to_synset(i) for i in sensekey]
                inst2ans[instid] = Answer(sensekey, lemma, pos)
        return inst2ans

    def test_instances(self):
        """
        Returns the test instances from SemEval2007 Coarse-grain WSD task.
        
        >>> coarse_wsd = SemEval2007_Coarse_WSD()
        >>> inst2ans = coarse_wsd.get_answers()
        >>> for inst in inst2ans:
        ...    print inst, inst2ans[inst]
        ...    break
        d004.s073.t013 answer(sensekey=[u'pointer%1:06:01::', u'pointer%1:06:00::', u'pointer%1:10:00::'], lemma=u'pointer', pos=u'n')
        """
        Instance = namedtuple('instance', 'id, lemma, word')
        test_file = io.open(self.test_file, 'r').read()
        inst2ans = self.get_answers()
        
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
                    yield inst, inst2ans[instid], unicode(sentence), unicode(document)
    
    def __iter__(self):
        """ Iterator function, duck-type of test_instances() """
        return self.test_instances()

