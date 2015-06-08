#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-15 alvations
# URL:
# For license information, see LICENSE.md

from distutils.core import setup

setup(
    name='pywsd',
    version='1.0',
    packages=['pywsd',],
    description='Python WSD',
    long_description='Python Implementations of Word Sense Disambiguation (WSD) technologies',
    license="MIT",
    install_requires = ['nltk', 'numpy']
)
