import logging
import logging.handlers

# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL


def logs_filter_example(log: logging.LogRecord) -> int:
    # if substring will be in log message it will be filtered and not displayed in logs
    if 'substring' in log.msg:
        return 0
    else:
        return 1


def init_logger(name) -> None:
    logger = logging.getLogger(name)
    msg_format = '{asctime} :: {levelname} :: {name}:{lineno} :: {message}'
    logger.setLevel(logging.DEBUG)
    streem_handler = logging.StreamHandler()
    streem_handler.setFormatter(logging.Formatter(fmt=msg_format, style='{'))
    streem_handler.setLevel(logging.DEBUG)
    # streem_handler.addFilter(logs_filter_example)  # filtering example

    # file_handler = logging.handlers.RotatingFileHandler(
    #     filename='logs.log',
    #     encoding='UTF-8',
    #     maxBytes=10485760,
    #     backupCount=2
    # )
    # file_handler.setFormatter(logging.Formatter(fmt=msg_format, style='{'))
    # file_handler.setLevel(logging.INFO)

    logger.addHandler(streem_handler)
    # logger.addHandler(file_handler)
