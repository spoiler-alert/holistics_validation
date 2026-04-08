import logging

FORMAT = "%(asctime)s %(levelname)-8s: %(message)s"
formatter = logging.Formatter(fmt=FORMAT)

logger = logging.getLogger("holistics_validation")
logger.setLevel(logging.INFO)


stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)  # only info and above go to the console
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
