from supervision.video.dataclasses import VideoInfo
from tqdm import tqdm


from typing import Generator

import cv2


def get_video_frames_generator(video_path: str) -> Generator[int, None, None]:
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_FPS, 5)
    fps = int(video.get(5))
    print("fps:", fps)
    if not video.isOpened():
        raise Exception(f"Could not open video at {video_path}")
    success, frame = video.read()
    while success:
        yield frame
        success, frame = video.read()
    video.release()


video_path = '.avi'
video_info = VideoInfo.from_video_path(video_path)
print(video_info)

generator = get_video_frames_generator(video_path)

for frame in tqdm(generator, total=video_info.total_frames):
    pass