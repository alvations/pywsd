#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest

from pywsd.lesk import simple_lesk, original_lesk, adapted_lesk, cosine_lesk


class TestHelloWorld(unittest.TestCase):
    def test_hello_word_len(self):
        self.assertEqual(len("Hello World"), 11)


class TestLesk(unittest.TestCase):
    def test_simple_lesk_default(self):
        bank_sents = [('I went to the bank to deposit my money', 'depository_financial_institution.n.01'),
                      ('The river bank was full of dead fishes', 'bank.n.01')]

        plant_sents = [('The workers at the industrial plant were overworked', 'plant.n.01'),
                       ('The plant was no longer bearing flowers', 'plant.v.01')]
        for sent, synset_name in bank_sents:
            self.assertEqual(simple_lesk(sent,'bank').name(), synset_name)
        for sent, synset_name in plant_sents:
            self.assertEqual(simple_lesk(sent,'plant').name(), synset_name)
