import cv2
import numpy as np
from supervision.draw.color import Color
from supervision.geometry.dataclasses import Rect

from .counter import CustomLineCounter
from .settings import CLASS_NAMES_DICT


class CustomLineCounterAnnotator:
    def __init__(
        self,
        thickness: float = 2,
        color: Color = Color.white(),
        text_thickness: float = 2,
        text_color: Color = Color.black(),
        text_scale: float = 0.5,
        text_offset: float = 1.5,
        text_padding: int = 10,
        class_name_dict={},
        video_info=[],
    ):
        self.thickness: float = thickness
        self.color: Color = color
        self.text_thickness: float = text_thickness
        self.text_color: Color = text_color
        self.text_scale: float = text_scale
        self.text_offset: float = text_offset
        self.text_padding: int = text_padding
        self.class_name_dict = class_name_dict
        self.video_info = video_info

    def annotate(
        self, frame: np.ndarray, line_counter: CustomLineCounter
    ) -> np.ndarray:
        cv2.line(
            frame,
            line_counter.vector.start.as_xy_int_tuple(),
            line_counter.vector.end.as_xy_int_tuple(),
            self.color.as_bgr(),
            self.thickness,
            lineType=cv2.LINE_AA,
            shift=0,
        )
        cv2.circle(
            frame,
            line_counter.vector.start.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )
        cv2.circle(
            frame,
            line_counter.vector.end.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )

        # report = ""
        # for key in line_counter.result_dict:
        #     class_name = CLASS_NAMES_DICT[key]
        #     in_count = line_counter.result_dict[key]["in"]
        #     out_count = line_counter.result_dict[key]["out"]
        #     report += f" | {class_name}: in {in_count} out {out_count}"
        # report += " |"

        # (report_width, report_height), _ = cv2.getTextSize(
        #     report, cv2.FONT_HERSHEY_SIMPLEX, self.text_scale, self.text_thickness
        # )

        # report_x = int(((self.video_info.width) - report_width) / 2)
        # report_y = int((150 + report_height) / 2 - self.text_offset * report_height)

        # report_background_rect = Rect(
        #     x=report_x,
        #     y=report_y - report_height,
        #     width=report_width,
        #     height=report_height,
        # ).pad(padding=self.text_padding)

        # cv2.rectangle(
        #     frame,
        #     report_background_rect.top_left.as_xy_int_tuple(),
        #     report_background_rect.bottom_right.as_xy_int_tuple(),
        #     self.color.as_bgr(),
        #     -1,
        # )

        # cv2.putText(
        #     frame,
        #     report,
        #     (report_x, report_y),
        #     cv2.FONT_HERSHEY_SIMPLEX,
        #     self.text_scale,
        #     self.text_color.as_bgr(),
        #     self.text_thickness,
        #     cv2.LINE_AA,
        # )
