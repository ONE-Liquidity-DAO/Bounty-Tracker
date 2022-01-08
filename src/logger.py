import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import coloredlogs


def setup_logging(log_level=logging.INFO,
                  file_log_level=logging.WARNING,
                  log_filename='./logs/default.log') -> Logger:
    """Setup root logger and quiet some levels."""
    logger = logging.getLogger()

    # Set log format to dislay the logger name
    # and to hunt down verbose logging modules
    fmt = "%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s'"

    # Use colored logging output for console
    coloredlogs.install(level=log_level, fmt=fmt, logger=logger)
    logging.getLogger("ccxt.base.exchange").setLevel(logging.INFO)

    # Disable all internal debug logging of requests and urllib3
    # E.g. HTTP traffic
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if log_filename:
        # Append to the log file
        handler = logging.handlers.RotatingFileHandler(
            log_filename, 'a', maxBytes=500000, backupCount=2)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(file_log_level)
        logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    logger = setup_logging()
    logger.info('test')
