#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Native Python Machine Learning Library: Perceptron Classifier
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

import numpy as np
import linear_classifier as lc

class Perceptron(lc.LinearClassifier):

    def __init__(self,nr_epochs = 10,learning_rate = 1, averaged = True):
        lc.LinearClassifier.__init__(self)
        self.trained = False
        self.nr_epochs = nr_epochs
        self.learning_rate = learning_rate
        self.averaged = averaged
        self.params_per_round = []

    def train(self,x,y):
        self.params_per_round = []
        x_orig = x[:,:]
        x = self.add_intercept_term(x)
        nr_x,nr_f = x.shape
        nr_c = np.unique(y).shape[0]
        w = np.zeros((nr_f,nr_c))
        ## Randomize the examples
        perm = np.random.permutation(nr_x)
        for epoch_nr in xrange(self.nr_epochs):
             for nr in xrange(nr_x):
                #print "iter %i" %( epoch_nr*nr_x + nr)
                inst = perm[nr]
                y_hat = self.get_label(x[inst:inst+1,:],w)
                if(y[inst:inst+1,0] != y_hat):
                    #Increase features of th e truth
                    w[:,y[inst:inst+1,0]] += self.learning_rate*x[inst:inst+1,:].transpose()
                    #Decrease features of the prediction
                    w[:,y_hat] += -1*self.learning_rate*x[inst:inst+1,:].transpose()
             self.params_per_round.append(w.copy())
             self.trained = True
             y_pred = self.test(x_orig,w)
             acc = self.evaluate(y,y_pred)
             self.trained = False
             print "Rounds: %i Accuracy: %f" %( epoch_nr,acc) 
        self.trained = True
        
        if(self.averaged == True):
            new_w = 0
            for old_w in self.params_per_round:
                new_w += old_w
            new_w = new_w / len(self.params_per_round)
            return new_w
        return w
