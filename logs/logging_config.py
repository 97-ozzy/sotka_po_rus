import logging
import sys
import os
from logging import StreamHandler, FileHandler # FileHandler нужен для JSON
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger # Теперь используем

LOG_LEVEL = logging.DEBUG
LOG_DIR = "logs"
LOG_FILENAME_TEXT = os.path.join(LOG_DIR, "bot.log")
#LOG_FILENAME_JSON = os.path.join(LOG_DIR, "bot.json.log") # Отдельный файл для JSON

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    if logger.handlers:
        for handler in logger.handlers[:]:
             logger.removeHandler(handler)

    # --- Стандартный текстовый форматер ---
    log_format_string = '%(asctime)s - %(levelname)-8s - %(name)-15s - %(filename)s:%(lineno)d - %(message)s'
    standard_formatter = logging.Formatter(log_format_string)

    # --- JSON Форматер ---
    # Можно настроить поля, которые попадут в JSON
    #json_format_string = '%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s'
    #json_formatter = jsonlogger.JsonFormatter(json_format_string)

    # --- Консольный обработчик (как в Варианте 1) ---
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(standard_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # --- Ротируемый текстовый файл (как в Варианте 1) ---
    rotating_file_handler = RotatingFileHandler(
        filename=LOG_FILENAME_TEXT, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    rotating_file_handler.setFormatter(standard_formatter)
    rotating_file_handler.setLevel(logging.WARNING)
    logger.addHandler(rotating_file_handler)

    # --- Файл для JSON логов ---
    # Можно использовать RotatingFileHandler и для JSON, если нужно
#    json_file_handler = FileHandler(filename=LOG_FILENAME_JSON, encoding='utf-8')
#    json_file_handler.setFormatter(json_formatter)
#    json_file_handler.setLevel(logging.DEBUG) # Пишем все в JSON
#    logger.addHandler(json_file_handler)

    logging.info("Logging setup complete. Console: INFO, Text File: DEBUG, JSON File: DEBUG")

