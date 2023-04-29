import logging
import sys

# Define a custom formatter that outputs the log message as plain text
class PlainTextFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()

# Create a logger and set the logging level to INFO
info_logger = logging.getLogger('info_log')
info_logger.setLevel(logging.INFO)

# Create a file handler that writes to a file named "info_log.txt"
info_file_handler = logging.FileHandler("info_log.txt", mode='w', encoding='utf-8')

# Set the formatter of the file handler to the custom plain text formatter
info_file_handler.setFormatter(PlainTextFormatter())

# Add the file handler to the logger
info_logger.addHandler(info_file_handler)

# Create a custom stream handler to redirect stdout to the logger
class LoggerStream:
    def __init__(self, info_logger, level):
        self.info_logger = info_logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            for line in message.splitlines():
                self.info_logger.log(self.level, line)

    def flush(self):
        pass

# Redirect stdout to the logger
sys.stdout = LoggerStream(info_logger, logging.INFO)

# Now any print statements will be logged as plain text in the "info_log.txt" file
# print("Hello, world!")
