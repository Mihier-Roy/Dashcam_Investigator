from pathlib import Path
from typing import List, Tuple
import filetype
import logging
from project_manager.project_datatypes import FileAttributes

logger = logging.getLogger(__name__)


def process_files(
    input_path: Path, setValue
) -> Tuple[List[FileAttributes], List[FileAttributes], List[FileAttributes]]:
    """
    This function identifies the file type and computes a FileAttributes object which is saved to the project file.
    """
    video_files = []
    image_files = []
    other_files = []
    current_index = 1
    for item in Path(input_path).rglob("*"):
        if item.is_file():
            setValue(current_index)
            current_index += 1
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
