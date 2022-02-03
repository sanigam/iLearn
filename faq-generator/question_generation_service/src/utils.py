import os
import json

# Primary setup for logging
import logging
import sys
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)s — %(name)s — %(funcName)s (%(lineno)d) — %(message)s"
)
# LOG_FILE = os.path.join(os.environ.get("LOG_DIR", "."), "application.log")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.DEBUG)
    return console_handler


# def get_file_handler():
#     file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
#     file_handler.setFormatter(FORMATTER)
#     return file_handler


# def get_file_handler():
#     file_handler = RotatingFileHandler(
#         LOG_FILE,
#         mode="a",
#         maxBytes=20 * 1024 * 1024,
#         backupCount=5,
#         encoding=None,
#         delay=0,
#     )
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(FORMATTER)
#     return file_handler


def get_named_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    # logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


logging.basicConfig(handlers=(get_console_handler(),), level=logging.WARNING)
