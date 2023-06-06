from logging import INFO
from logging import basicConfig, getLogger
from logging import Formatter, Logger, StreamHandler


from config import LOG_FILE_PATH, LOGGING_FORMAT


def init_logger(class_name: str) -> Logger:
    basicConfig(
        level=INFO,
        filename=LOG_FILE_PATH,
        format=LOGGING_FORMAT,
        datefmt='%H:%M:%S',
        filemode='w+'
    )

    stream_handler = StreamHandler()
    stream_handler.formatter = Formatter(LOGGING_FORMAT)

    logger = getLogger(class_name)
    logger.addHandler(stream_handler)

    return logger
