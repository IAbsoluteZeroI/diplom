#!/bin/sh
docker run --rm -d --name db --user root -p 5432:5432 -e POSTGRES_PASSWORD=root -e POSTGRES_USER=admin -e POSTGRES_DB=db -e PGDATA=postgres/data -e POSTGRES_INITDB_ARGS="-A md5" postgres:14.3
docker run --rm --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DB_HOST=db -e DISPLAY=$DISPLAY --link db absoiutezero/tracker-app:test2 python3 app.py
