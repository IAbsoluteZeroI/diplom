#!/bin/sh
apt update -y
apt upgrade -y
apt install g++ ffmpeg libsm6 libxext6 -y
mkdir postgres
mkdir postgres/data
#docker-compose up -d --build
pip install -r requirements.txt
cd app/utils/ByteTrack/
python setup.py develop
cd ../../../
python app.py
