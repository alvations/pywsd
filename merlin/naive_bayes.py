#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Native Python Machine Learning Library: Naive Bayes Classifer
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

import numpy as np
import linear_classifier as lc
from gaussian import *


class NaiveBayes(lc.LinearClassifier):

    def __init__(self,xtype="gaussian"):
        lc.LinearClassifier.__init__(self)
        self.trained = False
        self.xtype = xtype

    def train(self,x,y):
        nr_x,nr_f = x.shape
        nr_c = np.unique(y).shape[0]
        
        if(self.xtype == "gaussian"):
           params =  self.train_gaussian(x,y,nr_x,nr_f,nr_c)
        elif(self.xtype == "Multinomial"):
            print "Training a multinomial"
            params = self.train_multinomial(x,y,nr_x,nr_f,nr_c)
        else:
            print "Naive Bayes not implemented for this type of model of P(X|Y)"
        self.trained = True;
        return params


    ##########################
    ### Estimate mean and variance of
    ### Gaussian Distributions
    ### Note that the variance is shared for all
    ### classes
    ##########################
    def train_gaussian(self,x,y,nr_x,nr_f,nr_c):
        prior = np.zeros(nr_c)
        likelihood = np.zeros((nr_f,nr_c))
        classes = np.unique(y)
        means = np.zeros((nr_c,nr_f))
        variances = np.zeros((nr_c,nr_f))
        for i in xrange(nr_c):
            idx,_ = np.nonzero(y == classes[i])
            prior[i] = 1.0*len(idx)/len(y)
            for f in xrange(nr_f):
                g = estimate_gaussian(x[idx,f])
                means[i,f] = g.mean
                variances[i,f] = g.variance
        ## Take the mean of the covariance for each matric
        variances = np.mean(variances,1)
        params = np.zeros((nr_f+1,nr_c))
        for i in xrange(nr_c):
            params[0,i] = -1/(2*variances[i]) * np.dot(means[i,:],means[i,:]) + np.log(prior[i])
            
            params[1:,i] = (1/variances[i] * means[i]).transpose()
        return params

    

    ##########################
    ### Train a gaussian distribution
    ### Has one multinomial for each feature
    ##########################
    def train_multinomial(self,x,y,nr_x,nr_f,nr_c):
        prior = np.zeros(nr_c)
        ind_per_class = {}
        classes = np.unique(y)
        for i in xrange(nr_c):
            idx,_ = np.nonzero(y == classes[i])
            ind_per_class = idx
        likelihood = np.zeros((nr_f,nr_c))
        sums = np.zeros((nr_f,1))
        for i in xrange(nr_c):
            idx,_ = np.nonzero(y == classes[i]) 
            prior[i] = 1.0*len(idx)/len(y)

            value =  x[idx,:].sum(0)
            sums[:,0] += value
            likelihood[:,i] = value
                
        for f in xrange(nr_f):
            for i in xrange(nr_c):
                likelihood[f,i] = likelihood[f,i]/sums[f,0] 
        params = np.zeros((nr_f+1,nr_c))
        for i in xrange(nr_c):
            params[0,i] = np.log(prior[i])
            params[1:,i] = np.nan_to_num(np.log(likelihood[:,i]))
        return params