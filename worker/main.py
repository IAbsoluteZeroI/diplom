import argparse
import asyncio

from model.tracker import track_video
from supervision.geometry.dataclasses import Point

# start = Point(x=1200, y=750)
# end = Point(x=1100, y=230)
# track_video('kab24.avi', start, end)

# python3 main.py --file-path kab24.avi --camera-id 1 --start-xy 1200 750 --end-xy 1100 230
# python3 main.py --file-path lift.avi --camera-id 2 --start-xy 927 750 --end-xy 1100 227


async def main(file_path, camera_id, start, end):
    await track_video(file_path, start, end, camera_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track video.")
    parser.add_argument(
        "--file-path", type=str, required=True, help="Path to the video file"
    )
    parser.add_argument("--camera-id", type=int, required=True, help="ID of the camera")
    parser.add_argument(
        "--start-xy",
        type=str,
        nargs=2,
        metavar=("X", "Y"),
        help="Starting point in format X Y",
    )
    parser.add_argument(
        "--end-xy",
        type=str,
        nargs=2,
        metavar=("X", "Y"),
        help="Ending point in format X Y",
    )

    args = parser.parse_args()

    start = (
        Point(x=int(args.start_xy[0]), y=int(args.start_xy[1]))
        if args.start_xy
        else Point(x=1200, y=750)
    )
    end = (
        Point(x=int(args.end_xy[0]), y=int(args.end_xy[1]))
        if args.end_xy
        else Point(x=1100, y=230)
    )

    asyncio.run(main(args.file_path, args.camera_id, start, end))
