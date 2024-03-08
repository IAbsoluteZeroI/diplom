#!/bin/sh
mkdir postgres
mkdir postgres/data
sudo chown -R $USER:$USER postgres/data
pip install -r requirements.txt
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py