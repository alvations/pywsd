#!/usr/bin/env python -*- coding: utf-8 -*-

from lesk import simple_lesk

bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print "======== TESTING simple_lesk ===========\n"
print "Context:", bank_sents[0]
answer = simple_lesk(bank_sents[0],'bank')
print "Sense:", answer
print "Definition:",answer.definition
print

print "Context:", bank_sents[1]
answer = simple_lesk(bank_sents[1],'bank','n')
print "Sense:", answer
print "Definition:",answer.definition
print

print "Context:", plant_sents[0]
answer = simple_lesk(plant_sents[0],'plant','n', True)
print "Sense:", answer
print "Definition:",answer.definition
print

