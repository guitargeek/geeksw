#!/bin/bash

TEST_DATA_DIR="."

mkdir -p $TEST_DATA_DIR/lhe_data
cd $TEST_DATA_DIR/lhe_data
wget --no-check-certificate https://duck.jonaslan.de/geeksw-test-data/lhe_data/zzz_ft9.lhe.gz
wget --no-check-certificate https://duck.jonaslan.de/geeksw-test-data/lhe_data/zzz_ft9_3_events.lhe
wget --no-check-certificate https://duck.jonaslan.de/geeksw-test-data/lhe_data/zzz_ft9_0_events.lhe
cd ..

mkdir -p $TEST_DATA_DIR/nano_data
cd $TEST_DATA_DIR/nano_data
wget --no-check-certificate https://duck.jonaslan.de/geeksw-test-data/nano_data/wwz_double_lepton_filter.root
wget --no-check-certificate https://duck.jonaslan.de/geeksw-test-data/nano_data/wwz_single_lepton_filter.root
cd ..
