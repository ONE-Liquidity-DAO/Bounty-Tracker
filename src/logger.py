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

    # Quiet some internal logs
    logging.getLogger("dex_ohlcv.eventscanner").setLevel(logging.INFO)
    logging.getLogger("ccxt.base.exchange").setLevel(logging.INFO)

    # Disable logging of JSON-RPC requests and reploes
    logging.getLogger("web3.RequestManager").setLevel(logging.WARNING)
    logging.getLogger("web3.providers.HTTPProvider").setLevel(logging.WARNING)
    # logging.getLogger("web3.RequestManager").propagate = False

    # Disable all internal debug logging of requests and urllib3
    # E.g. HTTP traffic
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # IPython notebook internal
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Datadog tracer agent
    # https://ddtrace.readthedocs.io/en/stable/basic_usage.html
    logging.getLogger("ddtrace").setLevel(logging.INFO)

    # Flooding of OpenAPI spec debug notes on startup
    logging.getLogger("openapi_spec_validator").setLevel(logging.WARNING)

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
