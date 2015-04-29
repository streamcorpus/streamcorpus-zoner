'''streamcorpus-pipeline transform for generating line-based "zone" assignments

'''


#from streamcorpus import OffsetType, Offset
from __future__ import division
from features import fraction_stop_words_chars, fraction_punctuation


class zoner(object):


    def __init__(self, classifier):
        '''
        picks which zoner to use
        '''
        available_classifiers = {
            'simple': self.classify_simple,
            'window': self.classify_window

        }
        self.classify = available_classifiers[classifier]


    # def process_item(self, si, context=None):

    #     #tags = run_zoner(si.body.clean_visible)
    #     tags = self.classify(si.body.raw)
    #     for line_number, zone_number in tags:
    #         off = Offset(
    #             type=OffsetType.LINES,
    #             first=tag,
    #             length=1,
    #             value=zone_number,
    #         )
    #         #si.body.zones

    #         ## need to do something with off

    #     return si

    def classify_line_simple(self, line):
        '''
        A heuristic for classifying lines

        1 means 'body'
        0 means 'not_body'
        '''
        if fraction_stop_words_chars(line) > fraction_punctuation(line):
            return 1
        else:
            return 0

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

        Zones:
        1 means 'body'
        0 means 'not_body'
        '''
        simple_zones = list()
        for line in doc:
            simple_zones.append(self.classify_line_simple(line))

        ## simple window detector
        i = 0
        j = len(simple_zones) - 1
        proportion = sum(
                (zone == 1 for zone in simple_zones)
            ) / len(simple_zones)
        # print proportion, i, j
        while i < j:

            oldi = i
            for i in xrange(oldi+1, len(simple_zones)):
                if simple_zones[i] == 1:
                    break

            oldj = j
            for j in xrange(oldj-1, -1, -1):
                if simple_zones[j] == 1:
                    break

            new_proportion_shift_i = sum(
                (zone == 1 for zone in simple_zones[i:oldj+1])
            ) / len(simple_zones[i:oldj+1])

            new_proportion_shift_j = sum(
                (zone == 1 for zone in simple_zones[oldi:j+1])
            ) / len(simple_zones[oldi:j+1])

            if new_proportion_shift_i > new_proportion_shift_j:
                j = oldj
                new_proportion = new_proportion_shift_i
            else:
                i = oldi
                new_proportion = new_proportion_shift_j

            if new_proportion > thresh:
                break



        # print 

        # for idx, zone in enumerate(simple_zones):
        #     print idx, zone

        beginning = [0 for _ in xrange(i)]
        middle = [1 for _ in xrange(i, j + 1)] 
        end = [0 for _ in xrange(j+1, len(simple_zones))]

        zones = list()
        zones.extend(beginning)
        zones.extend(middle)
        zones.extend(end)

        return zones
        
