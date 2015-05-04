'''
Script for scoring sample data using zoning classification. 
'''
from __future__ import division

import argparse
import yakonfig
import dblogger

from zoner import zoner

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
        ## coarse-grain over the given labels which go from
        ## 0 to 3, with 2 being body
        if int(line[0]) == 2:
            labels.append(1)
        else:
            labels.append(0)
        data.append(line[2:])

    return labels, data

def score(zones, labels, positive=1):
    '''
    Compare the classification output in `zones' to the ground truth
    data in `labels'. Compute precision, recall, and f-score.

    `positive' sets the value of the zone that is taken to be positive
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'example', 
        help='an example file')
    args = yakonfig.parse_args(parser, [yakonfig, dblogger])
    example_file_name = args.example
    example_doc = open(example_file_name, 'r')

    ## separate the labels from the data
    labels, data = extract_labels(example_doc)

    ## classify example doc using simple zoner
    zoner_simple = zoner('simple')
    zones = zoner_simple.classify(data)
    scores = score(zones, labels)

    print 'Precision: %f, Recall: %f, F-score: %f' % \
            (scores['P'], scores['R'], scores['F'])

    ## classify example doc using window zoner
    zoner_simple = zoner('window')
    zones = zoner_simple.classify(data)
    scores = score(zones, labels)

    print 'Precision: %f, Recall: %f, F-score: %f' % \
            (scores['P'], scores['R'], scores['F'])

