#!/usr/bin/env python -*- coding: utf-8 -*-

from collections import namedtuple

from BeautifulSoup import BeautifulSoup as bsoup

from semeval2007_coarsegrain import *
from utils import remove_tags

def fileids():
    return  {'train': ['masaccio', 'computer_programming', 
                       'wsj_0105_mrg', 'wsj_0186_mrg', 'wsj_0239_mrg', 
                       'coarse_all_words', 'readme', 'sample_answer_file'],
             'test': ['sense_cluster_21_senses','fs_baseline_key', 
                      'dataset_21_test_key', 'scorer_pl']}
    
def sents(filename):
    for line in globals()[filename].split('\n'):
        yield line

def test_instances():
    """
    Returns the test instances from SemEval2007 Coarse-grain WSD task.
    
    USAGE:
    >>> for inst, sent, doc in test_instances():
    ...     print inst
    ...     print inst.id, inst.lemma, inst,word
    ...     break
    instance(id=u'd001.s001.t001', lemma=u'editorial', word=u'editorial')
    d001.s001.t001 editorial editorial
    """
    Instance = namedtuple('instance', 'id, lemma, word')
    for text in bsoup(coarse_all_words).findAll('text'):
        textid = text['id']
        document = " ".join([remove_tags(i) for i in str(text).split('\n') 
                             if remove_tags(i)])
        for sent in text.findAll('sentence'):
            sentence =  " ".join([remove_tags(i) for i in str(sent).split('\n') 
                             if remove_tags(i)])
            for instance in sent.findAll('instance'):
                instid = instance['id']
                lemma = instance['lemma']
                word = instance.text
                inst = Instance(instid, lemma, word)
                yield inst, unicode(sentence), unicode(document) 
                
for i in test_instances():
    print i