#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-17 alvations
# URL:
# For license information, see LICENSE.md

from distutils.core import setup

setup(
    name='pywsd',
    version='1.1.6',
    packages=['pywsd'],
    description='Python WSD',
    long_description='Python Implementations of Word Sense Disambiguation (WSD) technologies',
    url = 'https://github.com/alvations/pywsd',
    package_data={'pywsd': ['data/signatures/*.pkl',]},
    license="MIT",
    install_requires = ['nltk', 'numpy', 'pandas']
)
