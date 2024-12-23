import argparse
import asyncio

from supervision.geometry.dataclasses import Point

from model.tracker import track_video


async def main(file_path, camera_id, start, end, line_id):
    await track_video(file_path, start, end, camera_id, line_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track video.")
    parser.add_argument(
        "--file-path", type=str, required=True, help="Path to the video file"
    )
    parser.add_argument("--camera-id", type=int, required=True, help="ID of the camera")
    parser.add_argument("--line-id", type=int, required=True, help="ID of the line")
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

    asyncio.run(main(args.file_path, args.camera_id, start, end, args.line_id))
