# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

def setup_logger(name: str, log_file: Path, level=logging.INFO):
    """Настройка логгера с ротацией файлов"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Ротируемый файловый обработчик (10 MB, 3 бэкапа)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Консольный вывод
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Очистка старых обработчиков
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger