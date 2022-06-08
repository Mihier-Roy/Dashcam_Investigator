import logging
import logging.config
from pathlib import Path
import tempfile
from extract_metadata import (
    extract_metadata_loop,
    get_file_list,
    make_handlers,
)
import os


def main():
    logger = logging.getLogger(__name__)
    logger.info("Running dashcam investigator info")
    logger.info(f"Temp dir set : {tempfile.gettempdir()}")

    input_path = input("Enter a file path : ")
    input_path = Path(input_path)
    logger.debug(f"Obtained input path: {input_path}.")

    logger.debug(f"Beginning analysis of input directory.")
    video_list = get_file_list(input_directory=input_path)

    logger.debug("Video files identified: ")
    for video in video_list:
        print(f"Name: {video}")

    logger.debug(f"Beginning metadata extraction on {len(video_list)} files.")
    meta_list = make_handlers(
        video_name_list=video_list, temp_directory=tempfile.gettempdir()
    )
    extract_metadata_loop(meta_list, input_path)
    logger.debug("Metadata extraction completed!")


if __name__ == "__main__":
    # Create a logs directory in AppData\Local\DashcamInvestigator if it doesn't already exist
    appdata_local = os.getenv("LOCALAPPDATA")
    log_path = os.path.join(appdata_local, "DashcamInvestigator", "Logs")
    log_path = log_path.replace("\\", "/")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Setup logging based on log.conf
    logging.config.fileConfig("log.conf", defaults={"logPath": log_path})

    # Call main function
    main()
