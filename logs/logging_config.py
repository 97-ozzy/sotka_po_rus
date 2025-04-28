import logging
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

# Уровни логирования
LOG_LEVEL = logging.DEBUG  # Можно менять на INFO, WARNING или ERROR для уменьшения подробности


def setup_logging():
    # Получаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Настройка формата для логов в JSON
    log_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
    formatter = jsonlogger.JsonFormatter(log_format)

    # Обработчик для записи в файл (с ротацией)
    file_handler = RotatingFileHandler("logs/bot_errors.json", maxBytes=10 ** 6, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(LOG_LEVEL)

    # Обработчик для вывода в консоль
    stream_handler = StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(LOG_LEVEL)

    # Добавляем обработчики в логгер
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Информация о настройке логирования
    #logger.info("Logging setup complete with level: %s", logging.getLevelName(LOG_LEVEL))




# Запуск настройки логирования
setup_logging()