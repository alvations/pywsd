#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): SemEval REader API
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

import os, io
from collections import namedtuple

from BeautifulSoup import BeautifulSoup as bsoup
from pywsd.utils import remove_tags, semcor_to_synset

Instance = namedtuple('instance', 'id, lemma, word')
Term = namedtuple('term', 'id, pos, lemma, sense, type')
Word = namedtuple('word', 'id, text, sentid, paraid, term')
Answer = namedtuple('answer', 'sensekey, lemma, pos')


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
    def __init__(self, path='data/semeval2007_coarse_grain_wsd/'):
        self.path = path
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

    def yield_sentences(self):
        test_file = io.open(self.test_file, 'r').read()
        inst2ans = self.get_answers()
        for text in bsoup(test_file).findAll('text'):
            if not text:
                continue
            textid = text['id']
            context_doc = " ".join([remove_tags(i) for i in
                                    str(text).split('\n') if remove_tags(i)])
            for sent in text.findAll('sentence'):
                context_sent =  " ".join([remove_tags(i) for i in
                                      str(sent).split('\n') if remove_tags(i)])
                yield sent, context_sent, context_doc, inst2ans, textid

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
        for sent, context_sent, context_doc, inst2ans, textid in self.yield_sentences():
            for instance in sent.findAll('instance'):
                instid = instance['id']
                lemma = instance['lemma']
                word = instance.text
                inst = Instance(instid, lemma, word)
                yield inst, inst2ans[instid],
                unicode(context_sent), unicode(context_doc)

    def sentences(self):
        """
        Returns the instances by sentences, and yields a list of tokens,
        similar to the pywsd.semcor.sentences.

        >>> coarse_wsd = SemEval2007_Coarse_WSD()
        >>> for sent in coarse_wsd.sentences():
        >>>     for token in sent:
        >>>         print token
        >>>         break
        >>>     break
        word(id=None, text=u'Your', offset=None, sentid=0, paraid=u'd001', term=None)
        """
        for sentid, ys in enumerate(self.yield_sentences()):
            sent, context_sent, context_doc, inst2ans, textid = ys
            instances = {}
            for instance in sent.findAll('instance'):
                instid = instance['id']
                lemma = instance['lemma']
                word = instance.text
                instances[instid] = Instance(instid, lemma, word)

            tokens = []
            for i in sent: # Iterates through BeautifulSoup object.
                if str(i).startswith('<instance'): # BeautifulSoup.Tag
                    instid = sent.find('instance')['id']
                    inst = instances[instid]
                    answer = inst2ans[instid]
                    term = Term(instid, answer.pos, inst.lemma, answer.sensekey,
                                type='open')
                    tokens.append(Word(instid, inst.word,
                                       sentid, textid, term))
                else: # if BeautifulSoup.NavigableString
                    tokens+=[Word(None, w, sentid, textid, None)
                             for w in i.split()]
            yield tokens

    def __iter__(self):
        """ Iterator function, duck-type of test_instances() """
        return self.sentences()
