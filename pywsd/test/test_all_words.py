#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest

class TestAllWords(unittest.TestCase):
    def test_hello_word_len(self):
        self.assertEqual(len("Hello World"), 11)
