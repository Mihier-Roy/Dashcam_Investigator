import logging
from os import system
from pathlib import Path

logger = logging.getLogger(__name__)


def process_gps_data(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts GPS metadata from a video file and return the Path to the resulting GPX file
    """
    logger.debug(f"Extracting GPS data for -> {video_path.resolve()}")
    output_gpx = Path(output_dir, f"{video_path.name[0:-4]}.gpx")
    system(f"exiftool -p gpx.fmt -ee3 {video_path.resolve()} > {output_gpx.resolve()}")
    return str(output_gpx.resolve())


def process_file_meta(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts File metadata from a video file and return the Path to the resulting CSV
    """
    output_csv = Path(output_dir, f"{video_path.name[0:-4]}_fileinfo.csv")
    logger.debug(f"Extracting File metadata data for -> {video_path.resolve()}")
    system(
        f'exiftool -ee -FileType -filesize -MIMEType -d %d-%m-%Y" "%H:%M:%S -createDate -Duration -Format -Information -csv  {video_path.resolve()} >> {output_csv.resolve()}'
    )

    return str(output_csv.resolve())
