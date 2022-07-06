from csv import reader, writer
import logging
from pathlib import Path
from os import system

logger = logging.getLogger(__name__)


def process_gps_data(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts GPS metadata from a video file and return the Path to the resulting CSV
    """
    logger.debug(f"Extracting GPS data for -> {video_path.resolve()}")
    output_csv = Path(output_dir, f"{video_path.name[0:-4]}_gpsdata.csv")
    system(
        f'exiftool  -ee -csv -p "$GPSSpeed, $GPSLatitude, $GPSLongitude" -r -n {video_path.resolve()} >> {output_csv.resolve()}'
    )
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


def process_file_meta(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts File metadata from a video file and return the Path to the resulting CSV
    """
    output_csv = Path(output_dir, f"{video_path.name[0:-4]}_fileinfo.csv")
    logger.debug(f"Extracting File metadata data for -> {video_path.resolve()}")
    system(
        f'exiftool -ee -FileType -filesize -MIMEType -d %d-%m-%Y" "%H:%M:%S -createDate -Duration -Format -Information -csv  {video_path.resolve()} >> {output_csv.resolve()}'
    )
    logger.debug(f"File metadata available at -> {output_csv}")

    return str(output_csv.resolve())


def process_time_meta(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts Time metadata from a video file and return the Path to the resulting CSV
    """
    output_csv = Path(output_dir, f"{video_path.name[0:-4]}_timedata.csv")
    logger.debug(f"Extracting time metadata for -> {video_path.resolve()}")
    system(
        f'exiftool -ee -d %d-%m-%Y" "%H:%M:%S -gpsdatetime -s -s -s {video_path.resolve()} >> {output_csv.resolve()}'
    )
    logger.debug(f"Time metadata available at -> {output_csv}")

    return str(output_csv.resolve())
