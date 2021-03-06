'''
Features for document zoning classification.
'''
from __future__ import division
import os

import string
import argparse
import yakonfig
import dblogger

from nltk.corpus import stopwords

def fraction_whitespace(line):
    '''
    Feature that computes the fraction of the line that is white space.

    N.B. we treat empty lines as 100 percent whitespace.
    '''
    if len(line) == 0:
        return 1
    else:
        return line.count(' ')/len(line)

def fraction_punctuation(line):
    '''
    Feature that computes the fraction of the line that is punctuation.

    N.B. we treat empty lines as 0 percent punctuation.

    '''
    if len(line) == 0:
        return 0
    else:
        return sum([1 for x in line if x in set(string.punctuation)])/len(line)

def fraction_stop_words(line):
    '''
    Feature that computes the fraction of 1-grams on the line that consist of
    stop words.

    N.B. we treat empty lines as 0 percent.
    '''
    words = line.split()
    if len(words) == 0:
        return 0
    else:
        stop = set(stopwords.words('english'))
        return sum((1 for word in words if word in stop))/len(words)

def fraction_stop_words_chars(line):
    '''
    Feature that computes the fraction of characters on the line that
    participate in stop words.

    N.B. we treat empty lines as 0 percent.
    '''
    if len(line) == 0:
        return 0
    else:
        stop = set(stopwords.words('english'))
        return sum((len(word) for word in line.split() if word in stop))/len(line)

def fraction_words_capitalized(line):
    '''
    Feature that computes the fraction of words that are capitalized.

    N.B. we treat empty lines as 0 percent.
    '''
    words = line.split()
    if len(words) == 0:
        return 0
    else:
        stop = set(stopwords.words('english'))
        return sum((1 for word in words if word[0].isupper()))/len(words)

def fraction_capitalized_words_char(line):
    '''
    Feature that computes the fraction of characters on the line 
    participate in words that are capitalized.

    N.B. we treat empty lines as 0 percent.
    '''
    if len(line) == 0:
        return 0
    else:
        stop = set(stopwords.words('english'))
        return sum((len(word) for word in line.split() if word[0].isupper()))/len(line)

available_features = {
    'punctuation':fraction_punctuation,
    'whitespace': fraction_whitespace,
    'stop words': fraction_stop_words,
    'stop chars': fraction_stop_words_chars,
    'capital words': fraction_words_capitalized,
    'capital chars': fraction_capitalized_words_char
    }

def get_all_features(line):
    '''
    Takes a line of HTML and makes a dictionary of all features
    in `available_features'
    '''
    fv = dict()
    for feature_name, feature in available_features.iteritems():
        fv[feature_name] = feature(line)
    return fv

def convert_fv_to_string(fv, precision=1000):
    '''
    Takes a feature vector `fv' and converts it to a string
    representation of the features as required for seqlearn
    and the sklearn.feature_extraction.FeatureHasher (the 'hashing trick')

    `precision' stores how many digits the floats are rounded to in storing
    the features
    '''
    for feature, val in fv.iteritems():
        rounded_val = round(val*precision) ## nearest int between 0 and 100
        yield '%s:%d' % (feature, rounded_val)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'example', 
        help='an example file')
    args = yakonfig.parse_args(parser, [yakonfig, dblogger])
    example_file_name = args.example
    example_file = open(example_file_name, 'r')

    for line in example_file:

        ## the classification
        zone = int(line[0])

        ## the actual training data
        data = line[2:]

        out = ['label: %d' % zone] 

        fv = get_all_features(data)

        for feature_name, feature_val in fv.iteritems():
            out.append(' %s:%f' % (feature_name, feature_val))

        #print data
        if fraction_stop_words_chars(data) > fraction_punctuation(data):
            print ','.join(out)
            print data
            #pass
        elif zone == 2 and not fraction_stop_words_chars(data) > fraction_punctuation(data):
            #print data
            pass

        #print





