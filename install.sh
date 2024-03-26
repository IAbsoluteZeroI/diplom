#!/bin/sh
pip install -r requirements.txt
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py
