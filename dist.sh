#!/bin/sh
pip install wheel
python setup.py sdist bdist_wheel upload
