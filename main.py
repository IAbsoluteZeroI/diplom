import argparse
from supervision.geometry.dataclasses import Point
from worker.model.tracker import track_video

# start = Point(x=1200, y=750)
# end = Point(x=1100, y=230)
# track_video('kab24.avi', start, end)

def main(file_path, camera_id):
    start = Point(x=1200, y=750)
    end = Point(x=1100, y=230)

    track_video(file_path, start, end)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Track video.')
    parser.add_argument('--file-path', type=str, required=True, help='Path to the video file')
    parser.add_argument('--camera-id', type=int, required=True, help='ID of the camera')

    args = parser.parse_args()

    main(args.file_path, args.camera_id)
