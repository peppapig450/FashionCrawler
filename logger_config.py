# Copyright 2024 Nicholas Brady. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import logging
import logging.config
import os


def configure_logger():
    """
    Configure the logging system.

    This function sets up the logging configuration, including the log format,
    log file location, log level, and rotation settings.

    Returns:
        logger: The configured logger object.
    """

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "debug_formatter": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s - %(exc_info)s"
            },
            "info_formatter": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s- %(funcName)s - %(message)s"
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": os.path.join(logs_dir, "fashioncrawler.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 3,
                "formatter": "debug_formatter",
                "level": "DEBUG",
            }
        },
        "loggers": {
            "": {
                "handlers": ["file"],
                "level": "DEBUG",
            }
        },
        "filters": {
            "debug_filter": {"()": "logging.Filter", "name": "debug"},
            "info_filter": {"()": "logging.Filter", "name": "info"},
        },
    }

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(__name__)

    return logger
