from loguru import logger

from pathlib import Path
from datetime import datetime
import configparser

LOG_LEVELS = ['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']


def setup_logging(level='DEBUG'):
    """Setup logging_ for the project."""
    logger.remove()  # Remove default logger (stdout)    

    cur_time = datetime.now().strftime(
        "%Y%m%d-%H%M")  # get cur time for unique dir name

    config = configparser.ConfigParser()

    try:
        config.read('../../data/config/config.cfg')
        log_file = Path(config.get('Paths', 'log_path')) / cur_time / 'pipeline.log'
    except Exception as e1:
        try:
            config.read('ERKER2Phenopackets/data/config/config.cfg')
            log_file = Path(config.get('Paths', 'log_path')) / cur_time / 'pipeline.log'
        except Exception as e2:
            print(f"Could not find config file. \n {e1} \n {e2}")
            exit()

    # Log to a file     
    logger.add(log_file, level=level)

    # You can customize the log format as needed    
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format=logger_format,
        level=level
    )
