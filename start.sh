#!/bin/sh
mkdir postgres
mkdir postgres/data
#docker-compose up -d --build
pip install -r requirements.txt
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py