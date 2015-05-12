'''
tests for script for Zoner classification
'''
from __future__ import division
from __future__ import absolute_import

import os
import argparse
import yakonfig
import dblogger
import pytest

from streamcorpus import ZoneType, OffsetType, make_stream_item

import streamcorpus_zoner
from streamcorpus_zoner.zoner import Zoner
from streamcorpus_zoner.scorer import extract_labels, score



def test_classifier_by_score():
    '''
    scores an example doc and compares against known scores
    for the deterministic classifiers, and otherwise asserts
    scores are greater than zero
    '''

    streamcorpus_zoner_path = os.path.abspath(streamcorpus_zoner.__file__)
    test_data_path = os.path.dirname(streamcorpus_zoner_path) + '/../data/0.html'

    example_doc = open(test_data_path, 'r')

    ## separate the labels from the data
    labels, data = extract_labels(example_doc)

    ## need coarse grained labels for the zoners
    ## that can only classify body or not_body
    coarse_labels = list()
    for label in labels:
        if label != ZoneType.BODY:
            coarse_labels.append(ZoneType.UNZONED)
        else:
            coarse_labels.append(ZoneType.BODY)

    ## classify example doc using all zoners
    for zoner_name in Zoner.available_classifiers:
        current_zoner = Zoner(zoner_name)
        zones = current_zoner.classify(data)

        ## these zoners classify all zones
        if zoner_name == 'seqlearn':
            print 'Zoner: %s' % zoner_name
            for zi in xrange(4):
                zone = Zoner._map_training_data_to_ZoneType[zi]
                scores = score(zones, labels, positive=zone)
                print '\tZone: %s, Precision: %f, Recall: %f, F-score: %f' % \
                        (zone, scores['P'], scores['R'], scores['F'])

                ## this is not deterministic, but make sure they are positive
                for sc in scores:
                    assert sc > 0

        ## these can only classify body or not_body
        ## they compare to coarse_labels
        else:
            scores = score(zones, coarse_labels)
            print 'Zoner: %s, Precision: %f, Recall: %f, F-score: %f' % \
                (zoner_name, scores['P'], scores['R'], scores['F'])

            ## these are deterministic
            if zoner_name == 'simple':
                assert abs(scores['F'] - 0.6122448979591837) < 1e-14

            if zoner_name == 'window':
                assert abs(scores['F'] - 0.9491525423728813) < 1e-14

def test_as_streamcorpus_transform():
    '''
    Tests the Zoner.__call__ method and therefore the 
    Zoner.process_item method ensuring that this
    transform conforms to the thrift standard.
    '''
    ## create streamitem from file
    streamcorpus_zoner_path = os.path.abspath(streamcorpus_zoner.__file__)
    test_data_path = os.path.dirname(streamcorpus_zoner_path) + \
                     '/../data/4.html'
    example_doc = open(test_data_path, 'r')
    labels, data = extract_labels(example_doc)   
    data = ''.join(data)
    si = make_stream_item(None, 'test')
    si.body.clean_html = data.encode('utf-8')


    ## run zoner using all available zoners
    for zoner_name in Zoner.available_classifiers:
        zoner = Zoner(zoner_name)
        zoner(si, context=None)
        
        ## unpack the zones and determine that there are as many
        ## zone classifications as labels
        tot = 0
        zones = si.body.zones[zoner.classifier]
        for zt in zones:
            zone = zones[zt]
            tot += len(zone.offsets[OffsetType.CHARS])

        ## the way we encoode and decode creates an extra line at the end
        assert tot == len(labels) + 1 




