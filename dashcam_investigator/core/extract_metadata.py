import functools
import logging
import shutil
import subprocess
from pathlib import Path

from dashcam_investigator.constants import EXIFTOOL_TIMEOUT_SECONDS, GPX_FORMAT_FILE
from dashcam_investigator.exceptions import ExifToolError

logger = logging.getLogger(__name__)


@functools.cache
def _exiftool_path() -> str:
    path = shutil.which("exiftool")
    if path is None:
        raise ExifToolError("exiftool binary not found on PATH")
    return path


def process_gps_data(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts GPS metadata from a video file and returns the Path to the resulting GPX file.
    Raises ExifToolError if exiftool is missing, times out, or exits with a non-zero code.
    """
    logger.debug(f"Extracting GPS data for -> {video_path.resolve()}")
    output_gpx = output_dir / f"{video_path.stem}.gpx"
    cmd = [
        _exiftool_path(),
        "-p",
        GPX_FORMAT_FILE,
        "-ee3",
        str(video_path.resolve()),
    ]
    try:
        with output_gpx.open("w") as fh:
            result = subprocess.run(
                cmd,
                stdout=fh,
                stderr=subprocess.PIPE,
                timeout=EXIFTOOL_TIMEOUT_SECONDS,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        output_gpx.unlink(missing_ok=True)
        raise ExifToolError(
            f"exiftool timed out after {EXIFTOOL_TIMEOUT_SECONDS}s for {video_path.name}"
        ) from exc
    if result.returncode != 0:
        output_gpx.unlink(missing_ok=True)
        raise ExifToolError(
            f"exiftool failed for {video_path.name}: "
            f"{result.stderr.decode(errors='replace').strip()}"
        )
    return output_gpx


def process_file_meta(video_path: Path, output_dir: Path) -> Path:
    """
    Extracts file metadata from a video file and returns the Path to the resulting CSV.
    Raises ExifToolError if exiftool is missing, times out, or exits with a non-zero code.
    """
    output_csv = output_dir / f"{video_path.stem}_fileinfo.csv"
    logger.debug(f"Extracting file metadata for -> {video_path.resolve()}")
    cmd = [
        _exiftool_path(),
        "-ee",
        "-FileType",
        "-filesize",
        "-MIMEType",
        "-d",
        "%d-%m-%Y %H:%M:%S",
        "-createDate",
        "-Duration",
        "-Format",
        "-Information",
        "-csv",
        str(video_path.resolve()),
    ]
    try:
        with output_csv.open("w") as fh:
            result = subprocess.run(
                cmd,
                stdout=fh,
                stderr=subprocess.PIPE,
                timeout=EXIFTOOL_TIMEOUT_SECONDS,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        output_csv.unlink(missing_ok=True)
        raise ExifToolError(
            f"exiftool timed out after {EXIFTOOL_TIMEOUT_SECONDS}s for {video_path.name}"
        ) from exc
    if result.returncode != 0:
        output_csv.unlink(missing_ok=True)
        raise ExifToolError(
            f"exiftool failed for {video_path.name}: "
            f"{result.stderr.decode(errors='replace').strip()}"
        )
    return output_csv
