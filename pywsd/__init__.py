#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

from pywsd._wordnet import wn
from pywsd.lesk import *
from pywsd.baseline import *
from pywsd.similarity import *
from pywsd.allwords_wsd import disambiguate

__version__ = '1.3.0'
