import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def get_logger(file, level=logging.INFO, console=True):
    """Создание логгера"""
    root = logging.getLogger('asyncio')
    root.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(file, mode="a")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        root.addHandler(console_handler)

    return root


logger = get_logger('crawler.log')
