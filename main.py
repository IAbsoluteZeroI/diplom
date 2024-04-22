from supervision.geometry.dataclasses import Point
from worker.model.tracker import track_video

start = Point(x=1200, y=750)
end = Point(x=1100, y=230)


track_video('kab24.avi',start, end)
