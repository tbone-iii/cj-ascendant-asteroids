import logging
import logging.handlers

# Date format
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt=date_format)

# SQL Alchemy - redirect to a file instead of stdout
sqlalchemy_log_handler = logging.handlers.RotatingFileHandler(
    filename="sqlalchemy_unit_tests_log.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
)
sqlalchemy_log_handler.setFormatter(formatter)
sqlalchemy_log_handler.setLevel(logging.DEBUG)

sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.DEBUG)
sqlalchemy_logger.addHandler(sqlalchemy_log_handler)
