import logging
import os
import sys
import json
import datetime
from .config import LOG_FILENAME


class JSONFormatter(logging.Formatter):
    """JSONFormatter - formatter for python logging"""

    def __init__(self):
        super().__init__()

    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = {"msg": record.msg}

        if isinstance(record.msg, Exception):
            record.msg = {"exception": str(record.msg)}

        if "datetime" not in record.msg:
            record.msg["datetime"] = str(datetime.datetime.now())

        if "process_id" not in record.msg:
            record.msg["process_id"] = os.getpid()

        record.msg = json.dumps(record.msg)
        return super().format(record)


logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
main_logger = logging.getLogger("main")
main_logger.setLevel(logging.WARNING)

fileHandler = logging.FileHandler(LOG_FILENAME)
fileHandler.setFormatter(JSONFormatter())
fileHandler.setLevel(logging.INFO)
main_logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
main_logger.addHandler(consoleHandler)


def get_logger():
    return main_logger


default_logger = get_logger()
