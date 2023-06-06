from pathlib import Path
from datetime import datetime


ROOT_DIR_PATH = Path('.').absolute()

LOGGING_FORMAT = '%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s'
LOG_FILE_PATH = ROOT_DIR_PATH / 'logs' / f'{datetime.now().strftime("%d.%m.%Y_%H-%M")}-application.log'