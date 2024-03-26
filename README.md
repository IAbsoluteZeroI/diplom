# Docker
(inside linux/wsl)
```
bash docker.sh
```

# Build from Source

```
sudo apt update -y && sudo apt upgrade -y && sudo apt install g++ ffmpeg libsm6 libxext6 -y
conda create --name diplom-env python=3.10.12
conda activate diplom-env
bash install.sh
```

fix pyqt:

```
export QT_QPA_PLATFORM="xcb"
sudo apt install libxcb-xinerama0 libqt5x11extras5
```
