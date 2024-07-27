import logging
import logging.handlers

# Date format
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt=date_format)

# Discord - redirect to a file instead of stdout, take control of Discordpy's logging
discord_log_handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=3,
)
discord_log_handler.setFormatter(formatter)
discord_log_handler.setLevel(logging.DEBUG)

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.DEBUG)
discord_logger.addHandler(discord_log_handler)

# SQL Alchemy - redirect to a file instead of stdout
sqlalchemy_log_handler = logging.handlers.RotatingFileHandler(
    filename="sqlalchemy.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
)
sqlalchemy_log_handler.setFormatter(formatter)
sqlalchemy_log_handler.setLevel(logging.INFO)

sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.addHandler(sqlalchemy_log_handler)

# Ours
our_file_log_handler = logging.handlers.RotatingFileHandler(
    filename="article-overload.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
)
our_stderr_log_handler = logging.StreamHandler()
our_stderr_log_handler.setFormatter(formatter)

our_logger = logging.getLogger("overload")
our_logger.setLevel(logging.DEBUG)
our_logger.addHandler(our_stderr_log_handler)
our_logger.addHandler(our_file_log_handler)
