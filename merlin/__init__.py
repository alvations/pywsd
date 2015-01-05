#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Pure Python Machine Learning Library
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

"""
Merlin is a simple machine learning library, largely derived from LXMLS-toolkit
from https://github.com/LxMLS/lxmls-toolkit

This is to support python libraries that wants to rely on minimal dependencies.
"""

import linear_classifier
from svm import SVM
from naive_bayes import NaiveBayes
from mira import Mira
from perceptron import Perceptron


import util
from merlin.simple_data_set import SimpleDataSet