#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Native Python Machine Learning Library: SVM Classifier
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md


import numpy as np
from linear_classifier import LinearClassifier
from utils import *

class SVM(LinearClassifier):
    """ Linear SVM """
    def __init__(self,nr_epochs = 10, initial_step = 1.0, alpha = 1.0,regularizer = 1.0):
        LinearClassifier.__init__(self)
        self.trained = False
        self.nr_epochs = nr_epochs
        self.params_per_round = []
        self.initial_step = initial_step
        self.alpha = alpha
        self.regularizer = regularizer
        
    def train(self,x,y):
        self.params_per_round = []
        x_orig = x[:,:]
        x = self.add_intercept_term(x)
        nr_x,nr_f = x.shape
        nr_c = np.unique(y).shape[0]
        w = np.zeros((nr_f,nr_c))
        ## Randomize the examples
        perm = np.random.permutation(nr_x)
        #print "Starting Loop"
        t = 0
        for epoch_nr in xrange(self.nr_epochs):
            objective = 0.0
            for nr in xrange(nr_x):
                t = t+1
                learning_rate =  self.initial_step*np.power(t,-self.alpha)            
                inst = perm[nr]
                scores = self.get_scores(x[inst:inst+1,:],w)
                y_true = y[inst:inst+1,0]
                cost_augmented_loss = scores + 1 
                cost_augmented_loss[:,y_true] -= 1 
                y_hat = np.argmax(cost_augmented_loss,axis=1).transpose()
                objective += 0.5 * self.regularizer * l2norm_squared(w) - scores[:,y_true] + cost_augmented_loss[:,y_hat]
                w = (1-self.regularizer*learning_rate)*w
                w[:,y_true] += learning_rate*x[inst:inst+1,:].transpose()
                w[:,y_hat] -= learning_rate*x[inst:inst+1,:].transpose()
            self.params_per_round.append(w.copy())   
            self.trained = True
            objective /= nr_x
            y_pred = self.test(x_orig,w)
            acc = self.evaluate(y,y_pred)
            self.trained = False
            print "Epochs: %i Objective: %f" %( epoch_nr,objective)
            print "Epochs: %i Accuracy: %f" %( epoch_nr,acc)
        self.trained = True
        return w