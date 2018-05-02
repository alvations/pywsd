#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Deep stuff
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md

import tensorflow as tf
import tensorflow_hub as hub


# Import the Universal Sentence Encoder's TF Hub module
embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/1")
