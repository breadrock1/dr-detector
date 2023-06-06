from logging import INFO
from logging import basicConfig, getLogger
from logging import StreamHandler, Formatter

from cv2 import error
from cv2 import VideoCapture, GaussianBlur
from cv2 import absdiff, boundingRect, cvtColor, findContours, imshow, rectangle, threshold, waitKey
from cv2 import COLOR_RGB2GRAY
from cv2 import THRESH_BINARY, THRESH_OTSU
from cv2 import RETR_EXTERNAL, RETR_LIST, CHAIN_APPROX_SIMPLE

from numpy import random, median, uint8, array

from config import LOG_FILE_PATH, LOGGING_FORMAT
from queue_list import QueueList


basicConfig(
    level=INFO,
    filename=LOG_FILE_PATH,
    format=LOGGING_FORMAT,
    datefmt='%H:%M:%S',
    filemode='w+'
)

stream_handler = StreamHandler()
stream_handler.formatter = Formatter(LOGGING_FORMAT)

logger = getLogger(__name__)
logger.addHandler(stream_handler)


class DrDetector:

    def __init__(self, capture: VideoCapture, is_video_file: bool = False):
        self.frames_size = 20
        self.video_capture = capture
        self.is_video_file = is_video_file

        self.background_frame = None
        self.bg_frames_set = QueueList(self.frames_size)

    def run_processing(self):
        try:
            self._processing_stream()
        except error or Exception as err:
            logger.error(msg=f'Critical streaming error: {str(err)}')
        finally:
            self.video_capture.release()

    def _processing_stream(self):
        frame_iteration_enum = 0
        self.bg_frames_set.append(self.video_capture.read())
        self.bg_frames_set.append(self.video_capture.read())
        while self.video_capture.isOpened():
            try:
                _flag, _frame = self.video_capture.read()

                if not _flag:
                    waitKey(10)
                    continue

                if frame_iteration_enum % 2 != 0:
                    frame_iteration_enum += 1
                    continue

                # if len(self.bg_frames_set) > self.frames_size / 2:
                #     self.background_frame = self._generate_median_frame()
                #     self._check_moving_objects(_frame)

                if len(self.bg_frames_set) < self.frames_size:
                    self.bg_frames_set.append(_frame)
                    continue

                self.background_frame = self._generate_median_frame()
                self._check_moving_objects(_frame)

                frame_iteration_enum += 1
                if self.is_video_file:
                    waitKey(10)

            except error or Exception as err:
                logger.error(msg=f'Failed while streaming: {str(err)}')

    def _generate_median_frame(self) -> VideoCapture:
        # frame_indexes = random.randint(0, self.frames_size, size=25)
        # numpy_array = array(self.bg_frames_set.to_list)
        # random_frames = numpy_array.take(frame_indexes, axis=0)
        # frame_median = median(random_frames, axis=0).astype(dtype=uint8)

        frame_median = median(self.bg_frames_set.to_list, axis=0).astype(dtype=uint8)
        return cvtColor(frame_median, COLOR_RGB2GRAY)

    def _check_moving_objects(self, frame: VideoCapture):
        gray_frame_sample = cvtColor(src=frame, code=COLOR_RGB2GRAY)
        bg_removed_frame = absdiff(src1=gray_frame_sample, src2=self.background_frame)
        frame_blur = GaussianBlur(src=bg_removed_frame, ksize=(35, 35), sigmaX=0)
        ret, frame_threshold = threshold(src=frame_blur, thresh=100, maxval=255, type=THRESH_BINARY)
        # ret, frame_threshold = threshold(src=frame_blur, thresh=0, maxval=255, type=THRESH_BINARY + THRESH_OTSU)

        # imshow('Frame', frame_threshold)
        # -------------------------------------------------------------------------------------------------------
        contours, _ = findContours(image=frame_threshold.copy(), mode=RETR_LIST, method=CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, width, height = boundingRect(array=contour)
            rectangle(frame, (x, y), (x + width, y + height), (123, 0, 255), 2)

        imshow('Frame', frame)


if __name__ == '__main__':
    capture = VideoCapture('C:\\Users\\User\\Videos\\video_1.mp4')
    dr_detector = DrDetector(capture, is_video_file=True)
    dr_detector.run_processing()
