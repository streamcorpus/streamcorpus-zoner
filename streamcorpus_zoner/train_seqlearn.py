'''
Use seqlearn to train and test seqlearn as a HMM zoner
'''
from __future__ import division

from glob import glob

from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction import FeatureHasher

from features import get_all_features, convert_fv_to_string
from scorer import score

import pickle


def process_sequences(sequences, labels, seq_lengths):
    '''
    Takes an iterator over files `sequences' and processes all the sequences

    Extracts the labels (the first char on each sample) and stores them in
    the empty `labels' list.

    Counts the number of samples (i.e. lines) in each sequence and stores
    that in the empty `seq_lengths' list. Then, len(seq_lengths) should be
    the number of sequences.

    For each line in a sequence (after extracting the label and removing 
    the space char), processes each line into the appropriate
    input format, converting each line into a feature vector.

    Then, this converts that feature vector into a string to be hashed
    using sklearn.feature_extraction.FeatureHasher (the 'hashing trick')

    This returns (in addition to populating `labels' and `sequences')
    a generator of size total number of samples. Each item in the 
    generator is itself a generator over the feature-strings for
    each sample.
    '''

    for sequence_file in sequences:
        sequence = open(sequence_file, 'r')
        seq_labels = list()
        for idx, line in enumerate(sequence):
            label = int(line[0])
            seq_labels.append(label)

            data = line[2:]
            fv = get_all_features(data)
            fv_string = convert_fv_to_string(fv)
            yield fv_string

        labels.extend(seq_labels)
        seq_lengths.append(len(seq_labels))

def describe(X, lengths):
    print("{0} sequences, {1} tokens.".format(len(lengths), X.shape[0]))


def load_data(fh):
    '''
    Splits data into test and training sections in specified directory.

    Calls process_sequences on each set to generate the input
    and label vectors.

    Calls sklearn.feature_extraction.FeatureHasher (the 'hashing trick')
    to make sparse feature vectors

    `fh' is the FeatureHasher
    '''

    files = glob('../data/*.html')

    # 80% training, 20% test
    print 'Loading training data...'
    train_files = [f for i, f in enumerate(files) if i % 5 != 0]
    lengths_train = list()
    y_train = list()
    raw_X_train = process_sequences(train_files, y_train, lengths_train)
    X_train = fh.transform(raw_X_train)
    describe(X_train, lengths_train)
    train = (X_train, y_train, lengths_train)

    print 'Loading test data...'
    test_files = [f for i, f in enumerate(files) if i % 5 == 0]
    lengths_test = list()
    y_test = list()
    raw_X_test = process_sequences(test_files, y_test, lengths_test)
    X_test = fh.transform(raw_X_test)
    describe(X_test, lengths_test)
    test = (X_test, y_test, lengths_test)

    return train, test


if __name__ == "__main__":
    fh = FeatureHasher(n_features=(2 ** 16), input_type='string')

    ## augment to specify path
    train, test = load_data(fh)
    X_train, y_train, lengths_train = train
    X_test, y_test, lengths_test = test


    clf = StructuredPerceptron(verbose=True, max_iter=1000)
    print("Training %s" % clf)
    clf.fit(X_train, y_train, lengths_train)
    y_pred = clf.predict(X_test, lengths_test)

    ## save the model and the featurehasher
    output = open('seqlearn.pkl', 'wb' )
    pickle.dump((clf, fh) , output)
    output.close()

    ## score for each zone as the 'positive'
    ## in the f-score sense
    for zone in xrange(4):
        scores = score(y_pred, y_test, positive=zone)
        print 'Zone: %d, Precision: %f, Recall: %f, F-score: %f' % \
                (zone, scores['P'], scores['R'], scores['F'])
    print

    ## uncomment to diagnose specific errors
    ## get the test data to diagnose errors
    files = glob('../data/*.html')
    test_files = [f for i, f in enumerate(files) if i % 5 == 0]
    test_lines = list()
    for sequence_file in test_files:
        sequence = open(sequence_file, 'r')
        seq_labels = list()
        for line in sequence:
            test_lines.append(line)

    for idx in xrange(len(y_pred)):
        if y_pred[idx] != y_test[idx]:
            print 'prediction: %d, label: %d' % (y_pred[idx], y_test[idx])
            print test_lines[idx][2:]

    # for y in y_pred:
    #     print y





