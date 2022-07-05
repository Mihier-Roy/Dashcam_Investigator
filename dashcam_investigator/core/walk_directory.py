from pathlib import Path
import filetype
import logging

logger = logging.getLogger(__name__)


def walk_directory(input_dir: Path):
    """
    This function walks through a given input path and categorises files into 'video', 'image' or 'other' based on the file type.
    """
    for item in input_dir.rglob("*"):
        logger.debug(f"{item}")
        if item.is_file():
            file_type = filetype.guess_mime(item.resolve())
            if file_type is not None:
                if file_type.split("/")[0] == "video":
                    logger.debug(f"Video found : {item.name}")
                elif file_type.split("/")[0] == "image":
                    logger.debug(f"Image found : {item.name}")
            else:
                logger.debug(f"Other file found: {item.name}")
