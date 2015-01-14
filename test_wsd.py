#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD function tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print "======== TESTING simple_lesk ===========\n"
from pywsd.lesk import simple_lesk
print "#TESTING simple_lesk() ..."
print "Context:", bank_sents[0]
answer = simple_lesk(bank_sents[0],'bank')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print

print "#TESTING simple_lesk() with POS ..."
print "Context:", bank_sents[1]
answer = simple_lesk(bank_sents[1],'bank','n')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition # Using older version of NLTK.
print "Definition:", definition
print

print "#TESTING simple_lesk() with POS and stems ..."
print "Context:", plant_sents[0]
answer = simple_lesk(plant_sents[0],'plant','n', True)
print "Sense:", answer
try: definition = answer.definition()
except: definition = answer.definition
print "Definition:", definition
print

print "#TESTING simple_lesk() with nbest results" # i.e. output ranked synsets.
print "Context:", plant_sents[0]
answer = simple_lesk(plant_sents[0],'plant','n', True, nbest=True)
print "Senses ranked by #overlaps:", answer
best_sense = answer[0]
try: definition = best_sense.definition() 
except: definition = best_sense.definition
print "Definition:", definition
print

print "#TESTING simple_lesk() with nbest results and scores"
print "Context:", plant_sents[0]
answer = simple_lesk(plant_sents[0],'plant','n', True, \
                     nbest=True, keepscore=True)
print "Senses ranked by #overlaps:", answer
best_sense = answer[0][1]
try: definition = best_sense.definition()
except: definition = best_sense.definition
print "Definition:", definition
print

print "#TESTING simple_lesk() with nbest results and normalized scores"
print "Context:", plant_sents[0]
answer = simple_lesk(plant_sents[0],'plant','n', True, \
                     nbest=True, keepscore=True, normalizescore=True)
print "Senses ranked by #overlaps:", answer
best_sense = answer[0][1]
try: definition = best_sense.definition() 
except: definition = best_sense.definition
print "Definition:", definition
print

print "======== TESTING adapted_lesk ===========\n"
from pywsd.lesk import adapted_lesk

print "#TESTING adapted_lesk() ..."
print "Context:", bank_sents[0]
answer = adapted_lesk(bank_sents[0],'bank')
print "Sense:", answer
try: definition = answer.definition()
except: definition = answer.definition
print "Definition:", definition
print

print "#TESTING adapted_lesk() with pos, stem, nbest and scores."
print "Context:", bank_sents[0]
answer = adapted_lesk(bank_sents[0],'bank','n', True, \
                     nbest=True, keepscore=True)
print "Senses ranked by #overlaps:", answer
best_sense = answer[0][1]
try: definition = best_sense.definition() 
except: definition = best_sense.definition
print "Definition:", definition
print

print "======== TESTING cosine_lesk ===========\n"
from pywsd.lesk import cosine_lesk

print "#TESTING cosine_lesk() ..."
print "Context:", bank_sents[0]
answer = cosine_lesk(bank_sents[0],'bank')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition
print "Definition:", definition
print

print "#TESTING cosine_lesk() with nbest results..."
print "Context:", bank_sents[0]
answer = cosine_lesk(bank_sents[0],'bank', nbest=True)
print "Senses ranked by #overlaps:", answer
best_sense = answer[0][0]
try: definition = best_sense.definition() 
except: definition = best_sense.definition
print "Definition:", definition
print

print "======== TESTING baseline ===========\n"
from pywsd.baseline import random_sense, first_sense
from pywsd.baseline import max_lemma_count as most_frequent_sense

print "#TESTING random_sense() ..."
print "Context:", bank_sents[0]
answer = random_sense('bank')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition
print "Definition:", definition
print

print "#TESTING first_sense() ..."
print "Context:", bank_sents[0]
answer = first_sense('bank')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition
print "Definition:", definition
print

print "#TESTING most_frequent_sense() ..."
print "Context:", bank_sents[0]
answer = most_frequent_sense('bank')
print "Sense:", answer
try: definition = answer.definition() 
except: definition = answer.definition
print "Definition:", definition
print

print "======== TESTING similarity ===========\n"
from pywsd.similarity import max_similarity

for sim_choice in ["path", "lch", "wup", "res", "jcn", "lin"]:
    print "Context:", bank_sents[0]
    print "Similarity:", sim_choice 
    answer = max_similarity(bank_sents[0], 'bank', sim_choice, pos="n")
    print "Sense:", answer
    try: definition = answer.definition() 
    except: definition = answer.definition
    print "Definition:", definition
    print
