#!/bin/sh
mkdir postgres
mkdir postgres/data
pip install -r requirements.txt
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py