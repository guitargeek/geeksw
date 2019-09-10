#!/bin/bash

cd docs
sphinx-apidoc -f -o source ../geeksw
make html
cd ..

ssh rembserj@lxplus.cern.ch "rm -rf ~/eos/www/geeksw/docs/master"
scp -r docs/build/html rembserj@lxplus.cern.ch:~/eos/www/geeksw/docs/master
