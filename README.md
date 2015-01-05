streamcorpus-zoner
==================

streamcorpus-zoner is a streamcorpus-pipeline transform that provides
a trainable text document segmenter that identifies zones of a
document automatically using an SVM+HMM model.  It is based on
[SVM^light](http://svmlight.joachims.org/).

This python package provides a transform stage called `zoner` that can
be configured to chop out unwanted sections of
`StreamItem.body.clean_{html,visible}` before NER tagging.
