#!/usr/bin/python -*- coding: utf-8 -*-
#
# Merlin - Almost Native Python Machine Learning Library: ML utilities
#
# Copyright (C) 2014-2015 alvations
# URL:
# For license information, see LICENSE.md

import numpy as np
from itertools import izip
import operator

def sort_dic_by_value(dic,reverse=False):
    return sorted(dic.iteritems(), 
                  key=operator.itemgetter(1),
                  reverse=reverse)

def dict_max(dic):
    """
    Returns maximum value of a dictionary.
    """
    aux = dict(map(lambda item: (item[1],item[0]),dic.items()))
    if aux.keys() == []:
        return 0
    max_value = max(aux.keys())
    return max_value,aux[max_value]

def perp_2d(a):
    """
    Gets a perpendicualar line in 2D
    """
    res = 1./a
    res = res[:,] * [-1,1]
    return res


def l2norm(a):
    """
    L2 normalize and array
    """
    return np.sqrt(l2norm_squared(a))

def l2norm_squared(a):
    """
    L2 normalize squared
    """
    value = 0
    for i in xrange(a.shape[1]):
        value += np.dot(a[:,i],a[:,i])
    return value

def normalize_array(a,direction="column"):
    """
    Normalizes an array to sum to one, either column wise, 
    or row wise or the full array.
    
    *Directions*
        Column-wise - 0 default
        Row-wise - 1 default
        All - 2 default
    """
    b = a.copy()
    if(direction == "column"):
        sums = np.sum(b,0)
        return np.nan_to_num(b/sums)
    elif(direction == "row"):
        sums =np.sum(b,1)
        return  np.nan_to_num((b.transpose() / sums).transpose())
    elif(direction == "all"):
        sums = np.sum(b)
        return np.nan_to_num(b / sums)
    else:
        print "Error non existing normalization"
        return b