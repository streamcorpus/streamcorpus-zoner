'''
Script for scoring sample data using zoning classification. 
'''
from __future__ import division

import argparse
import yakonfig
import dblogger

from streamcorpus import ZoneType

from zoner import Zoner

def extract_labels(doc):
    '''
    to be run on labeled test data.
    strips the first character from each line into
    a list of labels. returns the label list and the 
    raw data.
    '''
    labels = list()
    data = list()
    for line in doc:
        label = int(line[0])
        zlabel = Zoner._map_training_data_to_ZoneType[label]
        labels.append(zlabel)
        data.append(line[2:])

    return labels, data

def score(zones, labels, positive=ZoneType.BODY):
    '''
    Compare the classification output in `zones' to the ground truth
    data in `labels'. Compute precision, recall, and f-score.

    `positive' sets the ZoneType that is taken to be positive
    (in the f-score sense)

    Everything else is taken to be negative.
    '''
    assert len(zones) == len(labels)

    TP = 0
    FN = 0
    TN = 0
    FP = 0

    for i in xrange(len(zones)):
        zone = zones[i]
        label = labels[i]
        TP += label == zone and label == positive
        TN += label == zone and label != positive
        FP += not label == zone and label != positive
        FN += not label == zone and label == positive

    P = TP / (TP + FP)
    R = TP / (TP + FN)
    F = 2*P*R / (P + R)

    return {'P': P, 'R': R, 'F': F}


