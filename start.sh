#!/bin/sh
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py