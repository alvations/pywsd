#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Native Python Machine Learning Library: Simple Data Set
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

"""
This class generates a 2D dataset with two classes, "positive" and "negative".
Each class follows a Gaussian distribution.
"""

import numpy as np

class SimpleDataSet:
    """ 
    A simple two dimentional dataset for visualization purposes. 
    The date set contains points from two gaussians with mean u_i and std_i
    """

    def __init__(self,nr_examples=100,g1 = [[-5,-5],1], g2 = [[5,5],1],balance=0.5,split=[0.8,0,0.2]):
        nr_positive = nr_examples*balance # number of examples of "positive" class
        nr_negative = nr_examples - nr_positive # number of examples of "negative" class
        self.mean1 = g1[0] # mean of positive class
        self.mean2 = g2[0] # mean of negative class
        self.variance1 = g1[1] # 
        self.variance2 = g2[1]
        self.balance = balance
        self.nr_points = nr_examples
        X_pos_1 = np.random.normal(g1[0][0],g1[1],[nr_positive,1])
        X_pos_2 = np.random.normal(g1[0][1],g1[1],[nr_positive,1])
        X_pos = np.hstack([X_pos_1,X_pos_2])
        X_neg_1 = np.random.normal(g2[0][0],g2[1],[nr_negative,1])
        X_neg_2 = np.random.normal(g2[0][1],g2[1],[nr_negative,1])
        X_neg = np.hstack([X_neg_1,X_neg_2])
        y_pos = np.zeros([nr_positive,1],dtype=np.int)
        y_neg = np.ones([nr_negative,1],dtype=np.int)
        X = np.vstack([X_pos, X_neg])
        y = np.vstack([y_pos, y_neg])

                      
        perm = np.random.permutation(nr_examples)
        self.split = split
        self.X = X[perm,:]
        self.y = y[perm]
        train_y,dev_y,test_y,train_X,dev_X,test_X = split_train_dev_test(self.X,self.y,split[0],split[1],split[2])
        self.train_X = train_X
        self.train_y = train_y
        self.dev_X = dev_X
        self.dev_y = dev_y
        self.test_X = test_X
        self.test_y = test_y

    def get_name(self):
        return "Simple Data Set -- Mean1= (%.2f,%.2f) Var1 = %.2f Mean2= (%.2f,%.2f) Var2= %.2f \nNr. Points=%.2f, Balance=%.2f Train-Dev-Test (%.2f,.%.2f,%.2f)"%(self.mean1[0] ,self.mean1[1], self.variance1, self.mean2[0], self.mean2[1], self.variance2, self.nr_points, self.balance, self.split[0],self.split[1],self.split[2])

    def get_bayes_optimal(self):
        params = np.zeros((3,2))
        p1 = self.balance
        p2 = 1.0 - self.balance
        params[0,0] = -1.0/(2.0*self.variance1) * np.dot(self.mean1,self.mean1) + np.log(p1)
        params[0,1] = -1.0/(2.0*self.variance2) * np.dot(self.mean2,self.mean2) + np.log(p2)
        params[1,0] = 1.0/self.variance1 * self.mean1[0]
        params[2,0] = 1.0/self.variance1 * self.mean1[1]
        params[1,1] = 1.0/self.variance2 * self.mean2[0]
        params[2,1] = 1.0/self.variance2 * self.mean2[1]
        ##print params
        return params
        
    def plot_data(self,params=np.array([]),name="Naive Bayes", print_bayes_opt = True):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        fig.suptitle(self.get_name())
        axis = fig.add_subplot(1,1,1)
        idx,_ = np.nonzero(self.train_y == 0)
        idx2,_ = np.nonzero(self.train_y == 1)
        idx3,_ = np.nonzero(self.test_y == 0)
        idx4,_ = np.nonzero(self.test_y == 1)
        axis.scatter(self.train_X[idx,0],self.train_X[idx,1],s=30,c="red",marker='s')
        axis.scatter(self.train_X[idx2,0],self.train_X[idx2,1],s=30,c="blue",marker='s')
        if(idx3.shape[0] > 0):
            axis.scatter(self.test_X[idx3,0],self.test_X[idx3,1],s=30,c="red",marker='o')
        if(idx4.shape[0] > 0):
            axis.scatter(self.test_X[idx4,0],self.test_X[idx4,1],s=30,c="blue",marker='o')
        ## Plot Bayes optimal
        if(print_bayes_opt):
            bayes_opt_params = self.get_bayes_optimal()
            self.add_line(fig,axis,bayes_opt_params, "Bayes Optimal","black")
        
        
        axis.legend()
#        fig.show()
        return fig,axis

    def add_line(self,fig,axis,params,name,colour):
        x_max = np.max(self.train_X)
        x_min = np.min(self.train_X)
        x = np.arange(x_min,x_max,0.1,dtype = "float")
        y_star = ((params[1,1]-params[1,0])*x + (params[0,1] - params[0,0]))/(params[2,0] -params[2,1])
        axis.plot(x,y_star,'g--',c=colour, label=name, linewidth=2)
        axis.legend()
#        fig.show()
        return fig,axis

    
    
def split_train_dev_test(X,y,train_per,dev_per,test_per):
    if(train_per + dev_per + test_per > 1):
        print "Train Dev Test split should sum to one"
        return
    dim = y.shape[0]
    split1 = int(dim*train_per)
    if(dev_per ==0):
        train_y,test_y = np.vsplit(y,[split1])
        dev_y = np.array([])
        train_X = X[0:split1,:]
        dev_X = np.array([])
        test_X = X[split1:,:]

    else:
        split2 = int(dim*(train_per+dev_per))
        print split2
        train_y,dev_y,test_y = np.vsplit(y,(split1,split2))
        train_X = X[0:split1,:]
        dev_X = X[split1:split2,:]
        test_X = X[split2:,:]
    return train_y,dev_y,test_y,train_X,dev_X,test_X