import configparser
import os
from pathlib import Path

from loguru import logger


def last_phenopackets() -> Path:
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    out_dirs = [
        Path(config.get('Paths', 'phenopackets_out_script')),
        Path(config.get('Paths', 'test_phenopackets_out_script'))
    ]

    subdirectories = []
    for out_dir in out_dirs:
        subdirectories = subdirectories + [
            os.path.join(out_dir, entry) for entry in os.listdir(out_dir)
            if os.path.isdir(os.path.join(out_dir, entry))
        ]

    sorted_directories = sorted(subdirectories, key=os.path.getmtime, reverse=True)
    path = Path(sorted_directories[0])

    if not path or not path.is_dir():
        logger.error('No path to data provided. Please provide a path to the data '
                     'as a command line argument.')
        raise ValueError('No path to data provided. Please provide a path to the '
                         'data as a command line argument.')

    return path
