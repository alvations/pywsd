#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md

from __future__ import absolute_import, print_function

import sys
import time


# Warm up the library.
print('Warming up PyWSD (takes ~10 secs)...', end=' ', file=sys.stderr)
start = time.time()

import pywsd.lesk
import pywsd.baseline
import pywsd.similarity

#import semcor
#import semeval

from pywsd.allwords_wsd import disambiguate

pywsd.lesk.simple_lesk('This is a foo bar sentence', 'bar')
print('took {} secs.'.format(time.time()-start), file=sys.stderr)
