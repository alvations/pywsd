#!/usr/bin/python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): Merlin tests
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

from merlin import SimpleDataSet 

# Create fake dataset
dataset = SimpleDataSet()
fig,axis = dataset.plot_data()

print "#################"
print "SVM"
print "#################"
from merlin import SVM
svm = SVM()
params_svm =  svm.train(dataset.train_X,dataset.train_y)
print params_svm.reshape(-1)
predict = svm.test(dataset.train_X,params_svm)
evaluation = svm.evaluate(predict,dataset.train_y)
predict2 = svm.test(dataset.test_X,params_svm)
evaluation2 = svm.evaluate(predict2,dataset.test_y)
print "Accuracy train: %f test: %f"%(evaluation,evaluation2)
fig, axis = dataset.add_line(fig,axis,params_svm,"SVM","brown")
print


print "#################"
print "Naive Bayes"
print "#################"
from merlin import NaiveBayes
nb = NaiveBayes()
params_nb = nb.train(dataset.train_X,dataset.train_y)
print params_nb.reshape(-1)
predict = nb.test(dataset.train_X,params_nb)
evaluation = nb.evaluate(predict,dataset.train_y)
predict2 = nb.test(dataset.test_X,params_nb)
evaluation2 = nb.evaluate(predict2,dataset.test_y)
print "Accuracy train: %f test: %f"%(evaluation,evaluation2)
fig,axis = dataset.add_line(fig,axis,params_nb,"Naive Bayes","red")
print



print "#################"
print "MIRA"
print "#################"
from merlin import Mira
mira = Mira()
params_mira =  mira.train(dataset.train_X,dataset.train_y)
print params_mira.reshape(-1)
predict = mira.test(dataset.train_X,params_mira)
evaluation = mira.evaluate(predict,dataset.train_y)
predict2 = mira.test(dataset.test_X,params_mira)
evaluation2 = mira.evaluate(predict2,dataset.test_y)
print "Accuracy train: %f test: %f"%(evaluation,evaluation2)
fig,axis = dataset.add_line(fig,axis,params_mira,"Mira","orange")
print


print "#################"
print "Perceptron"
print "#################"
from merlin import Perceptron
perc = Perceptron()
params_perc =  perc.train(dataset.train_X,dataset.train_y)
print params_perc.reshape(-1)
predict = perc.test(dataset.train_X,params_perc)
evaluation = perc.evaluate(predict,dataset.train_y)
predict2 = perc.test(dataset.test_X,params_perc)
evaluation2 = perc.evaluate(predict2,dataset.test_y)
print "Accuracy train: %f test: %f"%(evaluation,evaluation2)
fig,axis = dataset.add_line(fig,axis,params_perc,"Perceptron","blue")