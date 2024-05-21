FROM ubuntu:22.04

RUN mkdir /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libx11-dev \
    libxext-dev \
    libxtst-dev && \
    rm -rf /var/lib/apt/lists/*
RUN apt update && apt upgrade -y 
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y python3.10 python3.10-venv python3.10-dev
RUN apt install -y python3-pip
RUN apt install --fix-missing -y g++ ffmpeg libsm6 libxext6
COPY requirements.txt /app/
RUN pip install 'numpy<1.24'
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
#CMD ["python3", "./main.py --file-path "test.avi" --start-xy 1200 750 --end-xy 1100 230 --camera-id 123"]

RUN groupadd -r docker-gpus && adduser `whoami` docker-gpus
# RUN apt-get update && apt-get install -y nvidia-container-toolkit
# RUN systemctl enable --now nvidia-persistenced.service
# ENV NVIDIA_VISIBLE_DEVICES all
# ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
#
# CMD ["bash"]
