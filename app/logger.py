import logging
import os
from logging.handlers import RotatingFileHandler

# Opprett global logger
logger = logging.getLogger('app')

def setup_logger():
    if logger.handlers:  # Unngå å legge til handlers flere ganger
        return logger
        
    # Sett logging level
    logger.setLevel(logging.INFO)

    # Opprett logs-mappe hvis den ikke finnes
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Roter loggfiler når de når 1MB, behold 5 backup-filer
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024*1024, 
        backupCount=5
    )

    # Formater loggmeldinger
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Legg til console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Legg til handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 