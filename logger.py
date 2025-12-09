"""
Логирование для Prayer Tracker Bot
"""
import logging
import sys
from config import config

def setup_logger(name: str) -> logging.Logger:
    """Инициализирует logger с правильным форматом"""
    logger = logging.getLogger(name)
    
    # Получаем уровень логирования из конфига
    log_level_str = config.log_level.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    
    # Удаляем старые обработчики чтобы не было дубликатов
    logger.handlers.clear()
    
    # Добавляем новый обработчик в stdout
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
