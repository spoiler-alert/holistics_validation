import os
import logging
from logging.handlers import TimedRotatingFileHandler

FORMAT = "%(asctime)s %(levelname)-8s: %(message)s"
formatter = logging.Formatter(fmt=FORMAT)

logger = logging.getLogger("holistics_validation")
logger.setLevel(logging.DEBUG)

if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = TimedRotatingFileHandler(
    filename="logs/holistics_validation.log",
    when="d",
    interval=1,
    backupCount=20,
    utc=True,
)
file_handler.setLevel(
    logging.DEBUG
)  # everything gets output to the logging file so if something weird happens, someone can go back and look
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)  # only info and above go to the console
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
