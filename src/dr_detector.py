from cv2 import error, imshow, waitKey
from cv2 import VideoCapture, GaussianBlur
from cv2 import absdiff, cvtColor, threshold
from cv2 import contourArea, findContours
from cv2 import boundingRect, rectangle
from cv2 import COLOR_RGB2GRAY
from cv2 import THRESH_BINARY, THRESH_OTSU
from cv2 import RETR_EXTERNAL, CHAIN_APPROX_SIMPLE

from numpy import median, uint8

from src import init_logger
from src.queue_list import QueueList


class DrDetector:

    logger = init_logger(__name__)

    def __init__(self,
                 capture: VideoCapture,
                 frame_size: int = 20,
                 contour_min_size: int = 100,
                 is_video_file: bool = False):

        self.video_capture = capture
        self.frames_size = frame_size
        self.is_video_file = is_video_file
        self.contour_min_size = contour_min_size

        self.background_frame = None
        self.bg_frames_set = QueueList(self.frames_size)

    @classmethod
    def build_video_capture(cls, video_source: str or int) -> VideoCapture:
        return VideoCapture(video_source)

    def run_processing(self):
        try:
            self._processing_stream()
        except error or Exception as err:
            self.logger.error(msg=f'Critical streaming error: {str(err)}')
        finally:
            self.video_capture.release()

    def _processing_stream(self):
        _, _frame = self.video_capture.read()
        while self.video_capture.isOpened():
            try:
                _flag, _frame = self.video_capture.read()
                if not _flag or self.bg_frames_set.size < self.frames_size:
                    continue

                self.background_frame = self._generate_median_frame()
                self._check_moving_objects(_frame)
            except error or Exception as err:
                self.logger.error(msg=f'Failed while streaming: {str(err)}')

            finally:
                self.bg_frames_set.append(_frame)
                if self.is_video_file:
                    waitKey(10)

    def _generate_median_frame(self) -> VideoCapture:
        frame_median = median(self.bg_frames_set.to_list, axis=0).astype(dtype=uint8)
        return cvtColor(frame_median, COLOR_RGB2GRAY)

    def _check_moving_objects(self, frame: VideoCapture):
        gray_frame_sample = cvtColor(src=frame, code=COLOR_RGB2GRAY)
        bg_removed_frame = absdiff(src1=gray_frame_sample, src2=self.background_frame)
        frame_blur = GaussianBlur(src=bg_removed_frame, ksize=(11, 11), sigmaX=0)
        ret, thresh_frame = threshold(src=frame_blur, thresh=0, maxval=255, type=THRESH_BINARY + THRESH_OTSU)
        contours, _ = findContours(image=thresh_frame.copy(), mode=RETR_EXTERNAL, method=CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if contourArea(contour) >= self.contour_min_size:
                x, y, w, h = boundingRect(contour)
                rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        imshow('Frame', frame)
