FROM python:3.10.12
FROM nvcr.io/nvidia/tensorrt:24.04-py3

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# Устанавливаем зависимости для OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libx11-dev \
    libxext-dev \
    libxtst-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN python -m pip install pip==21.1.1
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
