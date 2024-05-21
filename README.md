```
python3 main.py --file-path kab24.avi --camera-id 1 --start-xy 1200 750 --end-xy 1100 230
python3 main.py --file-path lift.avi --camera-id 2 --start-xy 927 750 --end-xy 1100 227
```

```
docker run --rm --net=diplom_default diplom-worker python3 main.py --file-path kab24.avi --camera-id 1 --start-xy 1200 750 --end-xy 1100 230

docker run --rm --net=diplom_default diplom-worker python3 main.py --file-path lift.avi --camera-id 2 --start-xy 927 750 --end-xy 1100 227
```
