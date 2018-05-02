#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Deep stuff
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md

import os
import pickle

import pandas as pd

import tensorflow as tf
import tensorflow_hub as hub

# Import the Universal Sentence Encoder's TF Hub module
universal_encoder = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/1")
embedded_definitions_picklefile = os.path.dirname(os.path.abspath(__file__)) + '/data/signatures/universal_embedded_definitions.pkl'
embedded_definitions = pd.read_pickle(embedded_definitions_picklefile)

def embed_sentences(sentences):
    """
    :param sentences: Sentences to embed
    :type sentences: list(str)
    """
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        return session.run(embed(sentences))

def embed(sentence):
    return embed_sentences([sentence])[0]
