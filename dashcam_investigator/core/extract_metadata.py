from csv import reader, writer
import logging
from pathlib import Path
from os import system

# from metadata_classes import (
#     GPSMetadataExtractor,
#     TimeMetadataExtractor,
#     FileInfoMetadataExtractor,
# )

logger = logging.getLogger(__name__)


def process_gps_data(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts GPS metadata from a video file and return the Path to the resulting CSV
    """
    logger.debug(f"Extracting GPS data for -> {video_path.resolve()}")
    output_csv = Path(output_dir, f"{video_path.name[0:-4]}_gpsdata.csv")
    logger.debug(
        f'Executing -> exiftool  -ee -csv -p "$GPSSpeed, $GPSLatitude, $GPSLongitude" -r -n {video_path.resolve()} >> {output_csv.resolve()}'
    )
    system(
        f'exiftool  -ee -csv -p "$GPSSpeed, $GPSLatitude, $GPSLongitude" -r -n {video_path.resolve()} >> {output_csv.resolve()}'
    )
    logger.debug(f"Extracted GPS data for -> {video_path}")
    trim_data(output_csv, output_dir)
    logger.debug(f"GPS data available at -> {output_csv}")

    return str(output_csv.resolve())


def trim_data(output_csv: Path, output_dir: Path):
    """
    Removes rows in the exiftool csv output for gpsdata which can cause errors later in the code
    """
    temp_csv = Path(output_dir, f"{output_csv.name}.tmp")

    with output_csv.open("r") as csvfile_read:
        with temp_csv.open(
            "w",
            newline="",
        ) as csvfile_write:
            csv_writer = writer(csvfile_write)
            for row in reader(csvfile_read):
                if set(row).intersection(["SourceFile"]):
                    continue
                else:
                    csv_writer.writerow(row)
    output_csv.unlink()
    temp_csv.rename(output_csv)


# def make_handlers(video_name_list: list, temp_directory: str) -> list:
#     # Takes in a list of video names and temp directory, and makes a list of 3 metadata handlers for each video name.
#     # Returns the list of metadata handlers
#     metadata_handler_list = []
#     for video in video_name_list:
#         metadata_handler_list.append(
#             GPSMetadataExtractor(video=video, temp_directory=temp_directory)
#         )
#         metadata_handler_list.append(
#             TimeMetadataExtractor(video=video, temp_directory=temp_directory)
#         )
#         metadata_handler_list.append(
#             FileInfoMetadataExtractor(video=video, temp_directory=temp_directory)
#         )
#     return metadata_handler_list


# """
# TODO: Add a function to perform a check for each of the tags to extract.
# This way, runtime errors can be avoided and the tool can produce a verifiable result each time.
# """


# def extract_metadata_loop(metadata_handler_list: list, input_directory: str):
#     # Takes in a list of metadata handlers and calls their extract_metadata() methods
#     for metadata_handler in metadata_handler_list:
#         metadata_handler.extract_metadata(input_directory)
