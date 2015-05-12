'''streamcorpus-pipeline transform for generating line-based "zone" assignments
   and stores them in StreamItem.body.zones

'''
from __future__ import division

import os
import pickle

from streamcorpus import OffsetType, Offset, Zone, ZoneType

from features import fraction_stop_words_chars, fraction_punctuation
from features import get_all_features, convert_fv_to_string



class Zoner(object):

    def __init__(self, classifier):
        '''
        picks which zoner to use
        '''
        self.classifier_map ={
        'simple':self.classify_simple,
        'window':self.classify_window,
        'seqlearn':self.classify_seqlearn
        }

        assert(set(Zoner.available_classifiers) == set(self.classifier_map.keys()))

        self.classifier = classifier
        self.classify = self.classifier_map[self.classifier]

        if self.classifier == 'seqlearn':
            currrent_dir = os.path.dirname(os.path.abspath(__file__))
            pkl_file = open(currrent_dir + '/seqlearn.pkl', 'r')
            (self.clf, self.fh) = pickle.load(pkl_file)
            pkl_file.close()

    ## static list of available classifiers
    available_classifiers = ['simple', 'window', 'seqlearn']

    ## static mapping of line labels in training data to ZoneType
    _map_training_data_to_ZoneType = {
        0: ZoneType.HEADER,
        1: ZoneType.TITLE,
        2: ZoneType.BODY,
        3: ZoneType.FOOTER
    }

    def __call__(self, si, context):
        si = self.process_item(si, context)
        return si

    def process_item(self, si, context=None):
        '''
        runs the zoner on a stream item and stores the zones
        and offsets in StreamItem.body.zones
        '''
        if not si.body or not si.body.clean_html:
            return si

        if not si.body.zones:
            si.body.zones = dict()

        if not self.classifier in si.body.zones:
            si.body.zones[self.classifier] = dict()

        zone_dict = si.body.zones[self.classifier]

        doc_as_string = si.body.clean_html.decode('utf-8')
        doc = doc_as_string.split('\n')
        tags = self.classify(doc)

        char_idx = 0
        for idx, line in enumerate(doc):
            tag = tags[idx]
            if not tag in zone_dict:
                zone_dict[tag] = Zone(zone_type=tag, offsets=dict())
                zone_dict[tag].offsets[OffsetType.CHARS] = list()

            ## add new zone tag/offset to zone
            off = Offset(
                type=OffsetType.CHARS,
                first=char_idx,
                length=len(line),
            )
            zone_dict[tag].offsets[OffsetType.CHARS].append(off)

            ## accumulate the line to update char index
            char_idx += len(line)

        return si

    def classify_line_simple(self, line):
        '''
        A heuristic for classifying lines
        '''
        if fraction_stop_words_chars(line) > fraction_punctuation(line):
            return ZoneType.BODY
        else:
            return ZoneType.UNZONED

    def classify_simple(self, doc):
        '''
        Uses the line based simple heuristic classifier to classify a document
        '''
        zones = list()
        for line in doc:
            zones.append(self.classify_line_simple(line))
        return zones

    def classify_window(self, doc, thresh=0.2):
        '''
        Uses the line based simple heuristic classifier and the tries
        to look at windows to pick out the interval that contains the body.

        `thresh' sets the threshold proportion of lines classified as body 
        '''
        simple_zones = list()
        for line in doc:
            simple_zones.append(self.classify_line_simple(line))

        ## simple window detector
        i = 0
        j = len(simple_zones) - 1
        proportion = sum(
                (zone == ZoneType.BODY for zone in simple_zones)
            ) / len(simple_zones)
        # print proportion, i, j
        while i < j:

            oldi = i
            for i in xrange(oldi+1, len(simple_zones)):
                if simple_zones[i] == ZoneType.BODY:
                    break

            oldj = j
            for j in xrange(oldj-1, -1, -1):
                if simple_zones[j] == ZoneType.BODY:
                    break

            new_proportion_shift_i = sum(
                (zone == ZoneType.BODY for zone in simple_zones[i:oldj+1])
            ) / len(simple_zones[i:oldj+1])

            new_proportion_shift_j = sum(
                (zone == ZoneType.BODY for zone in simple_zones[oldi:j+1])
            ) / len(simple_zones[oldi:j+1])

            if new_proportion_shift_i > new_proportion_shift_j:
                j = oldj
                new_proportion = new_proportion_shift_i
            else:
                i = oldi
                new_proportion = new_proportion_shift_j

            if new_proportion > thresh:
                break

        beginning = [ZoneType.UNZONED for _ in xrange(i)]
        middle = [ZoneType.BODY for _ in xrange(i, j + 1)] 
        end = [ZoneType.UNZONED for _ in xrange(j+1, len(simple_zones))]

        zones = list()
        zones.extend(beginning)
        zones.extend(middle)
        zones.extend(end)

        return zones
    
    def classify_seqlearn(self, doc):
        '''
        Uses the seqlearn trained classifier to classify a doc.

        First convert the doc to the correct input format to the
        model. Then classify.
        '''
        features, doc_len = self.get_seqlearn_features(doc)
        lengths = [doc_len] ## since this can be used to classify many
        zones = self.clf.predict(features, lengths)
        #print zones
        return zones

    def get_seqlearn_features(self, sequence):
        '''
        Return the feature representation of `sequence' in
        the sparse-matrix seqlearn required format.

        Also return the length (i.e. number of lines) of 
        the sequence.
        '''
        x_raw = list()
        for sample in sequence:
            fv = get_all_features(sample)
            fv_string = convert_fv_to_string(fv)
            x_raw.append(fv_string)
        doc_len = len(x_raw)
        x_sparse = self.fh.transform(x_raw)
        return x_sparse, doc_len
