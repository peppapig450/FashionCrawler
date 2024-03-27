import logging
import os


class MyLogger:
    def __init__(self, log_file="logs/FashionCrawler.log"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create a formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Create the logging directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Create a file handler and set level and formatter
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Create a console handler and set level and formatter
        # console_handler = logging.StreamHandler()
        #  console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(formatter)

        # self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(self, message)
