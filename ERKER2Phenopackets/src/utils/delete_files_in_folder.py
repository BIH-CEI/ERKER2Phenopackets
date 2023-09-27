from pathlib import Path
from typing import Union, List
from loguru import logger


def delete_files_in_folder(dirs: Union[Path, List[Path]], file_extension: str = None):
    """Deletes all files in a folder

    This function deletes all files in a folder. If a file extension is given,
    only files with that file extension are deleted.

    :param dirs: Path to the folder or a list of paths to folders
    :type dirs: Union[Path, List[Path]]
    :param file_extension: File extension of the files that should be deleted
    :type file_extension: str
    """
    if isinstance(dirs, Path):
        dirs = [dirs]

    if file_extension:
        logger.info(f"Starting the delete_files_in_folder method with "
                    f"file extension {file_extension}")
    else:
        logger.info("Starting the delete_files_in_folder method")

    for directory in dirs:
        logger.info(f"Starting deletion in directory: {directory}")
        for file in directory.iterdir():
            logger.trace('iteration')
            if file.is_file():
                logger.trace(f"Found file {file}")
                logger.debug(f'{file_extension=}, '
                             f'{(file_extension in file.suffix)=}')
                if file_extension and file_extension in file.suffix:
                    logger.trace(f"Deleting the file {file}")
                    file.unlink()

    logger.info("Finished the delete_files_in_folder method")
