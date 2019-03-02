![Geeksw](res/geeksw.png?raw=true "Geeksw logo")
</br>
Python package to facilitate High Energy Physics analysis work with focus on the CMS experiment.

[![Build Status](https://travis-ci.com/guitargeek/geeksw.svg?branch=master)](https://travis-ci.com/guitargeek/geeksw)

## Introduction

In the CMS experiment, battle tested workflows create user friendly datasets for all collaborators to analyze. A well maintained software release, called [CMSSW](https://github.com/cms-sw/cmssw), provides all the (mostly C++) code to do so. However, after all the event data is ready in columnar data formats like [NanoAOD](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD), there is much less consensus within the collaboration on the framework to analyze this data with. Many groups have their own C++ based analysis frameworks which plug into CMSSW, but in times where the Python ecosystem for data analysis is so vast and powerful, some people believe that all analysis work should be done with Python libraries.

Analyzing CMS data in Python is made possible by powerful standard libraries like numpy, matplotlib, scipy and pandas, machine learling specific libraries like sklearn, keras or pytorch and more specific libraries coming from the HEP comminity like uproot, uproot-methods and awkward-array. On top of all that, jupyter-notebooks provide interactive environments for the actual work, which make it possible to write analysis code with markdown comments in between that is alomst as easy as english, making review processes much simpler. In fact, analysis with Python can even be faster than basic analyses with C++, since the columar instead of row (event) oriented paradigm allow for a log of optimizations like parallelism. The geeksw package builds on this existing ecosystem and offers functionailty that often used in HEP analyses in general, but also functionality which is more specific to analysis work within the CMS collaboration.

The following sections will give an overview on the features of geeksw. It is targeted to have as much documentation within the code as possible, but the main way how features are explained are example notebooks in the dedicated examples directory.

## Plotting

## Analysis framework

## Physics tools

## Utilities

## NanoAOD data loading
