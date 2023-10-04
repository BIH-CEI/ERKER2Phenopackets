import configparser
import os
from pathlib import Path

from loguru import logger


def last_phenopackets_dir() -> Path:
    """Returns the path to the last created phenopackets directory.

    This function returns the path to the last created phenopackets directory.

    :return: Path to the last created phenopackets directory
    :rtype: Path
    """
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    out_dirs = [
        Path(config.get('Paths', 'phenopackets_out_script')),
        Path(config.get('Paths', 'test_phenopackets_out_script'))
    ]

    return last_created_dir(*out_dirs)


def last_created_dir(*args):
    """Returns the path to the last created directory.

    This function returns the path to the last created directory from a sequence of
    paths.

    Example:
        >>> last_created_dir(Path('path/to/dir1'), Path('path/to/dir2'))
        Path('path/to/dir1')

    :param args: Sequence of paths
    :type args: Tuple[Path]
    :return: Path to the last created directory
    :rtype: Path
    """
    out_dirs = list(args)
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
