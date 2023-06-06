from argparse import ArgumentParser
from sys import argv

from cv2 import VideoCapture

from src.dr_detector import DrDetector


def parse_arguments():
    argument_parser = ArgumentParser(
        prog='Dr. Detector',
        usage='python3 launch.py { web | <path-to-file> }',
        add_help=True,
        allow_abbrev=True
    )

    sub_arg_parser = argument_parser.add_subparsers(title='Script Modes', dest='mode', required=True)
    sub_arg_parser.add_parser('web', help='Allows to open web camera stream.')
    file_arg = sub_arg_parser.add_parser('file', help='Launch vide file processing.')
    file_arg.add_argument('file_path', help='Path to video file')

    return argument_parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    video_source = 0 if arguments.mode == 'web' else arguments.file_path
    dr_detector = DrDetector(VideoCapture(video_source), is_video_file=True)
    dr_detector.run_processing()

