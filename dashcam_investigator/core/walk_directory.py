from pathlib import Path
from typing import Tuple, List
import filetype
import logging
from project_manager.project_datatypes import FileAttributes

logger = logging.getLogger(__name__)


def walk_directory(
    input_dir: Path,
) -> Tuple[List[FileAttributes], List[FileAttributes], List[FileAttributes]]:
    """
    This function walks through a given input path and categorises files into 'video', 'image' or 'other' based on the MIME type.
    """
    video_files: list[FileAttributes] = []
    image_files: list[FileAttributes] = []
    other_files: list[FileAttributes] = []
    # Iterate recursively through all the files in a directory
    for item in input_dir.rglob("*"):
        logger.debug(f"{item}")
        if item.is_file():
            file_type = filetype.guess_mime(item.resolve())
            if file_type is not None:
                if file_type.split("/")[0] == "video":
                    logger.debug(f"Video found : {item.name}")
                    video_files.append(FileAttributes(item))
                elif file_type.split("/")[0] == "image":
                    logger.debug(f"Image found : {item.name}")
                    image_files.append(FileAttributes(item))
            else:
                logger.debug(f"Other file found: {item.name}")
                other_files.append(FileAttributes(item))

    return video_files, image_files, other_files
