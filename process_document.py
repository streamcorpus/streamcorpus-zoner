'''
Transform a labeled html document to the correct format 
for processing by SVMhmm. Computes the relevant features
and prepares the input training file.

The directory containing the data is given as a command line
argument, and the output is written to stdout.
'''
from __future__ import division
import os

import string
import argparse
import yakonfig
import dblogger

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



available_features = [
    fraction_punctuation,
    fraction_whitespace,
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'directory', 
        help='directory where the training files live')
    args = yakonfig.parse_args(parser, [yakonfig, dblogger])
    directory = args.directory


    for qid, example_file_name in enumerate(os.listdir(directory)):

        ## qid is the example number (SVMhmm) convention, not mine
        example_file = open(directory + '/' + example_file_name, 'r')


        for line in example_file:

            ## the classification
            zone = int(line[0])

            ## the actual training data
            data = line[2:]

            out = ['%d qid:%d' % (zone + 1, qid + 1)] ## because this indexes 
                                                      ## by 1 and everything 
                                                      ## is terrible

            for featnum, feature in enumerate(available_features):
                out.append(' %d:%f' % (featnum + 1, feature(data)))

            print ''.join(out)




