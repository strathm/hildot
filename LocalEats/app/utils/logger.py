import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(log_directory, 'app.log'), maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='app/logs/app.log',  # Path to your log file
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_event(message, level='info'):
    """Logs an event with a specific level (info, warning, error)."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if level == 'info':
        logging.info(f'{timestamp} - {message}')
    elif level == 'warning':
        logging.warning(f'{timestamp} - {message}')
    elif level == 'error':
        logging.error(f'{timestamp} - {message}')
    else:
        logging.debug(f'{timestamp} - {message}')

logger = setup_logger()