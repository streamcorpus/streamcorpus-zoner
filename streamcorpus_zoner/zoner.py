'''streamcorpus-pipeline transform for generating line-based "zone" assignments

'''


#from streamcorpus import OffsetType, Offset
from features import fraction_stop_words_chars, fraction_punctuation


class zoner(object):


    def __init__(self, classifier):
        '''
        picks which zoner to use
        '''
        available_classifiers = {'simple': self.classify_simple}
        self.classify = available_classifiers[classifier]


    # def process_item(self, si, context=None):

    #     tags = run_zoner(si.body.clean_visible)
    #     for line_number, zone_number in tags:
    #         off = Offset(
    #             type=OffsetType.LINES,
    #             first=tag,
    #             length=1,
    #             value=zone_number,
    #         )
    #         #si.body.zones

    def classify_line_simple(self, line):
        '''
        A heuristic for classifying lines
        '''
        if fraction_stop_words_chars(line) > fraction_punctuation(line):
            return 'body'
        else:
            return 'not_body'

    def classify_simple(self, doc):
        '''
        Uses the line based simple heuristic classifier to classify a document
        '''
        zones = list()
        for line in doc:
            zones.append(self.classify_line_simple(line))
        return zones