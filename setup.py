#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-17 alvations
# URL:
# For license information, see LICENSE.md

from distutils.core import setup

from setuptools import setup
with open("README.md","r") as fh:
    long_description= fh.read()

  
setup(
    name='pywsd',
    version='1.2.4',
    packages=['pywsd'],
    description='Python WSD',
    long_description= long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/alvations/pywsd',
    package_data={'pywsd': ['data/signatures/*.pkl',]},
    license="MIT",
    install_requires = [
        'nltk',
        'numpy',
        'pandas',
        'wn==0.0.23',
        'six'
    ]
)
